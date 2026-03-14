import 'dart:io';

import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:go_router/go_router.dart';
import 'package:image_picker/image_picker.dart';

import '../../../core/api/models/order_models.dart';
import '../../../core/router/app_routes.dart';
import '../bloc/order_bloc.dart';
import '../bloc/order_event.dart';
import '../bloc/order_state.dart';
import '../widgets/risk_warning_dialog.dart';

class OrderUploadScreen extends StatelessWidget {
  const OrderUploadScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return BlocProvider(
      create: (_) => OrderBloc(),
      child: const _OrderUploadView(),
    );
  }
}

class _OrderUploadView extends StatefulWidget {
  const _OrderUploadView();

  @override
  State<_OrderUploadView> createState() => _OrderUploadViewState();
}

class _OrderUploadViewState extends State<_OrderUploadView> {
  final ImagePicker _picker = ImagePicker();
  final GlobalKey<FormState> _formKey = GlobalKey<FormState>();
  final TextEditingController _restaurantController = TextEditingController();
  final TextEditingController _amountController = TextEditingController();
  final TextEditingController _foodContentController = TextEditingController();

  final List<String> _selectedImages = [];
  static const int _maxImages = 2;

  @override
  void dispose() {
    _restaurantController.dispose();
    _amountController.dispose();
    _foodContentController.dispose();
    super.dispose();
  }

  Future<void> _pickFromCamera() async {
    if (_selectedImages.length >= _maxImages) {
      _showMessage('En fazla $_maxImages görsel seçebilirsiniz.');
      return;
    }

    try {
      final file = await _picker.pickImage(
        source: ImageSource.camera,
        maxWidth: 1280,
        imageQuality: 80,
      );
      if (file == null || file.path.isEmpty) return;

      setState(() {
        _selectedImages.add(file.path);
      });
      _resetDraftState();
    } catch (error) {
      _showMessage(error.toString().replaceFirst('Exception: ', ''));
    }
  }

  Future<void> _pickFromGallery() async {
    if (_selectedImages.length >= _maxImages) {
      _showMessage('En fazla $_maxImages görsel seçebilirsiniz.');
      return;
    }

    try {
      final remaining = _maxImages - _selectedImages.length;
      if (remaining > 1) {
        final files = await _picker.pickMultiImage(
          maxWidth: 1280,
          imageQuality: 80,
        );
        if (files.isEmpty) return;

        final filePaths = files
            .take(remaining)
            .map((file) => file.path)
            .where((path) => path.isNotEmpty)
            .toList();

        if (filePaths.isEmpty) return;

        setState(() {
          _selectedImages.addAll(filePaths);
        });
      } else {
        final file = await _picker.pickImage(
          source: ImageSource.gallery,
          maxWidth: 1280,
          imageQuality: 80,
        );
        if (file == null || file.path.isEmpty) return;

        setState(() {
          _selectedImages.add(file.path);
        });
      }

      _resetDraftState();
    } catch (error) {
      _showMessage(error.toString().replaceFirst('Exception: ', ''));
    }
  }

  void _removeImage(int index) {
    setState(() {
      _selectedImages.removeAt(index);
    });
    _resetDraftState();
  }

  void _resetDraftState() {
    _restaurantController.clear();
    _amountController.clear();
    _foodContentController.clear();
    context.read<OrderBloc>().add(const OrderFlowResetRequested());
  }

  void _syncDraft(OrderParseResponse response) {
    _restaurantController.text = response.restaurantName ?? '';
    _amountController.text = response.totalAmount != null
        ? response.totalAmount!.toStringAsFixed(2)
        : '';
    _foodContentController.text = response.foodContent ?? '';
  }

  void _showMessage(String message) {
    if (!mounted) return;
    ScaffoldMessenger.of(context)
      ..hideCurrentSnackBar()
      ..showSnackBar(
        SnackBar(content: Text(message)),
      );
  }

  void _parseReceipts() {
    if (_selectedImages.isEmpty) {
      _showMessage('Önce en az bir görsel seçin.');
      return;
    }

    context.read<OrderBloc>().add(
          OrderReceiptParseRequested(filePaths: List<String>.from(_selectedImages)),
        );
  }

  void _confirmOrder(OrderParseResponse parsedOrder) {
    final isValid = _formKey.currentState?.validate() ?? false;
    if (!isValid) return;

    final amountText = _amountController.text.trim();
    final normalizedAmount = amountText.replaceAll(',', '.');
    final totalAmount = normalizedAmount.isEmpty
        ? null
        : double.tryParse(normalizedAmount);

    if (amountText.isNotEmpty && totalAmount == null) {
      _showMessage('Tutar alanı geçerli bir sayı olmalı.');
      return;
    }

    final request = OrderConfirmRequest(
      restaurantName: _restaurantController.text.trim(),
      totalAmount: totalAmount,
      foodContent: _foodContentController.text.trim().isEmpty
          ? null
          : _foodContentController.text.trim(),
      rawOcrText: parsedOrder.rawOcrText,
      ocrConfidence: parsedOrder.ocrConfidence,
      warnings: parsedOrder.warnings,
      receiptDate: parsedOrder.receiptDate,
      items: parsedOrder.items,
    );

    context
        .read<OrderBloc>()
        .add(OrderConfirmationRequested(request: request));
  }

  void _showRiskWarning(OrderParseResponse response) {
    final riskWarning = response.warnings.where((warning) {
      return warning.contains('riskli restoran') || warning.contains('Dikkat');
    }).cast<String?>().firstWhere(
          (warning) => warning != null && warning.isNotEmpty,
          orElse: () => null,
        );

    if (riskWarning == null) return;

    var restaurantName = response.restaurantName ?? 'Bilinmeyen Restoran';
    final match = RegExp(r'Dikkat:\s*(.+?)\s*riskli').firstMatch(riskWarning);
    if (match != null && match.group(1) != null) {
      restaurantName = match.group(1)!.trim();
    }

    WidgetsBinding.instance.addPostFrameCallback((_) {
      if (!mounted) return;
      RiskWarningDialog.show(
        context,
        restaurantName: restaurantName,
        riskReason: riskWarning,
      );
    });
  }

  void _startNewFlow() {
    setState(() {
      _selectedImages.clear();
    });
    _resetDraftState();
  }

  @override
  Widget build(BuildContext context) {
    return BlocConsumer<OrderBloc, OrderState>(
      listenWhen: (previous, current) {
        return previous.status != current.status ||
            previous.parsedOrder != current.parsedOrder ||
            previous.errorMessage != current.errorMessage;
      },
      listener: (context, state) {
        if (state.status == OrderStatus.ocrSuccess && state.parsedOrder != null) {
          _syncDraft(state.parsedOrder!);
          _showRiskWarning(state.parsedOrder!);
        }

        if (state.status == OrderStatus.error && state.errorMessage != null) {
          _showMessage(state.errorMessage!);
        }

        if (state.status == OrderStatus.confirmed && state.confirmedOrder != null) {
          _showMessage('Sipariş başarıyla kaydedildi.');
        }
      },
      builder: (context, state) {
        final isUploading = state.status == OrderStatus.uploading;
        final isConfirming = isUploading && state.parsedOrder != null;
        final isParsing = isUploading && state.parsedOrder == null;

        return Scaffold(
          appBar: AppBar(
            title: const Text('Fiş Okut'),
            backgroundColor: Colors.orange,
            foregroundColor: Colors.white,
          ),
          body: SingleChildScrollView(
            padding: const EdgeInsets.all(20),
            child: state.confirmedOrder != null
                ? _buildSuccessView(state.confirmedOrder!)
                : Column(
                    crossAxisAlignment: CrossAxisAlignment.stretch,
                    children: [
                      _buildIntroCard(),
                      const SizedBox(height: 16),
                      if (_selectedImages.isNotEmpty) ...[
                        _buildThumbnailRow(),
                        const SizedBox(height: 16),
                      ],
                      if (!isUploading) ...[
                        if (_selectedImages.length < _maxImages) ...[
                          OutlinedButton.icon(
                            onPressed: _pickFromCamera,
                            icon: const Icon(Icons.camera_alt),
                            label: const Text('Kamera ile çek'),
                          ),
                          const SizedBox(height: 12),
                          OutlinedButton.icon(
                            onPressed: _pickFromGallery,
                            icon: const Icon(Icons.photo_library_outlined),
                            label: Text(
                              _selectedImages.isEmpty
                                  ? 'Galeriden seç'
                                  : 'Galeriden ekle',
                            ),
                          ),
                        ],
                        if (_selectedImages.isNotEmpty) ...[
                          const SizedBox(height: 16),
                          FilledButton.icon(
                            onPressed: _parseReceipts,
                            icon: const Icon(Icons.document_scanner_outlined),
                            label: Text(
                              _selectedImages.length == 1
                                  ? 'OCR Sonucunu Hazırla'
                                  : 'OCR Sonucunu Hazırla (${_selectedImages.length} görsel)',
                            ),
                            style: FilledButton.styleFrom(
                              backgroundColor: Colors.orange,
                              foregroundColor: Colors.white,
                              padding: const EdgeInsets.symmetric(vertical: 16),
                            ),
                          ),
                        ],
                      ],
                      if (isParsing) ...[
                        const SizedBox(height: 20),
                        const _LoadingCard(
                          title: 'OCR sonucu hazırlanıyor',
                          subtitle: 'Fiş okunuyor ve düzenlenebilir taslak oluşturuluyor...',
                        ),
                      ],
                      if (state.parsedOrder != null) ...[
                        const SizedBox(height: 20),
                        _buildConfirmationForm(
                          state.parsedOrder!,
                          isConfirming: isConfirming,
                          errorMessage: state.status == OrderStatus.error
                              ? state.errorMessage
                              : null,
                        ),
                      ],
                    ],
                  ),
          ),
        );
      },
    );
  }

  Widget _buildIntroCard() {
    return Card(
      color: Colors.orange.shade50,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Icon(Icons.receipt_long, color: Colors.orange.shade800),
                const SizedBox(width: 10),
                const Expanded(
                  child: Text(
                    'Fiş taslağı oluştur',
                    style: TextStyle(fontSize: 17, fontWeight: FontWeight.w700),
                  ),
                ),
              ],
            ),
            const SizedBox(height: 10),
            const Text(
              'Fiş veya ekran görüntüsü yükleyin. Sistem OCR ile verileri çıkarır, ancak sipariş siz onaylamadan kaydedilmez.',
            ),
            const SizedBox(height: 8),
            Text(
              'Uzun fişler için en fazla $_maxImages görsel seçebilirsiniz.',
              style: TextStyle(color: Colors.grey.shade700),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildConfirmationForm(
    OrderParseResponse parsedOrder, {
    required bool isConfirming,
    required String? errorMessage,
  }) {
    final receiptDateText = parsedOrder.receiptDate != null
        ? parsedOrder.receiptDate!.toLocal().toString().substring(0, 16)
        : 'Tespit edilemedi';

    return Form(
      key: _formKey,
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          Card(
            elevation: 0,
            shape: RoundedRectangleBorder(
              borderRadius: BorderRadius.circular(18),
              side: BorderSide(color: Colors.orange.shade100),
            ),
            child: Padding(
              padding: const EdgeInsets.all(18),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    children: [
                      Container(
                        padding: const EdgeInsets.all(10),
                        decoration: BoxDecoration(
                          color: Colors.orange.shade100,
                          borderRadius: BorderRadius.circular(12),
                        ),
                        child: Icon(
                          Icons.fact_check_outlined,
                          color: Colors.orange.shade900,
                        ),
                      ),
                      const SizedBox(width: 12),
                      const Expanded(
                        child: Text(
                          'OCR sonucu onay bekliyor',
                          style: TextStyle(fontSize: 18, fontWeight: FontWeight.w700),
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 10),
                  Text(
                    'Aşağıdaki alanları kontrol edin. Bu adım tamamlanmadan sipariş veritabanına kaydedilmez.',
                    style: TextStyle(color: Colors.grey.shade700),
                  ),
                  const SizedBox(height: 18),
                  TextFormField(
                    controller: _restaurantController,
                    decoration: const InputDecoration(
                      labelText: 'Restoran adı',
                      prefixIcon: Icon(Icons.storefront_outlined),
                      border: OutlineInputBorder(),
                    ),
                    validator: (value) {
                      if (value == null || value.trim().isEmpty) {
                        return 'Restoran adı zorunlu.';
                      }
                      return null;
                    },
                  ),
                  const SizedBox(height: 14),
                  TextFormField(
                    controller: _amountController,
                    keyboardType: const TextInputType.numberWithOptions(decimal: true),
                    decoration: const InputDecoration(
                      labelText: 'Toplam tutar',
                      hintText: 'Örn: 245.90',
                      prefixIcon: Icon(Icons.payments_outlined),
                      suffixText: 'TL',
                      border: OutlineInputBorder(),
                    ),
                    validator: (value) {
                      if (value == null || value.trim().isEmpty) {
                        return null;
                      }

                      final normalized = value.trim().replaceAll(',', '.');
                      return double.tryParse(normalized) == null
                          ? 'Geçerli bir tutar girin.'
                          : null;
                    },
                  ),
                  const SizedBox(height: 14),
                  TextFormField(
                    controller: _foodContentController,
                    minLines: 2,
                    maxLines: 4,
                    decoration: const InputDecoration(
                      labelText: 'Yemek içeriği',
                      prefixIcon: Icon(Icons.fastfood_outlined),
                      border: OutlineInputBorder(),
                    ),
                  ),
                  const SizedBox(height: 16),
                  Wrap(
                    spacing: 8,
                    runSpacing: 8,
                    children: [
                      _InfoChip(
                        icon: Icons.auto_awesome,
                        label:
                            'OCR güveni %${parsedOrder.ocrConfidence.toStringAsFixed(1)}',
                      ),
                      _InfoChip(
                        icon: Icons.event_outlined,
                        label: 'Fiş tarihi: $receiptDateText',
                      ),
                      if (parsedOrder.restaurantId != null)
                        _InfoChip(
                          icon: Icons.verified_outlined,
                          label: 'Mevcut restoran eşleşti',
                        ),
                    ],
                  ),
                  if (parsedOrder.warnings.isNotEmpty) ...[
                    const SizedBox(height: 16),
                    ...parsedOrder.warnings.map(
                      (warning) => Container(
                        width: double.infinity,
                        margin: const EdgeInsets.only(bottom: 8),
                        padding: const EdgeInsets.all(12),
                        decoration: BoxDecoration(
                          color: Colors.orange.shade50,
                          borderRadius: BorderRadius.circular(12),
                          border: Border.all(color: Colors.orange.shade200),
                        ),
                        child: Row(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Icon(
                              Icons.warning_amber_rounded,
                              size: 18,
                              color: Colors.orange.shade900,
                            ),
                            const SizedBox(width: 8),
                            Expanded(child: Text(warning)),
                          ],
                        ),
                      ),
                    ),
                  ],
                  if (parsedOrder.items.isNotEmpty) ...[
                    const SizedBox(height: 16),
                    const Text(
                      'Algılanan kalemler',
                      style: TextStyle(fontWeight: FontWeight.w700),
                    ),
                    const SizedBox(height: 8),
                    ...parsedOrder.items.map(
                      (item) => ListTile(
                        dense: true,
                        contentPadding: EdgeInsets.zero,
                        leading: CircleAvatar(
                          radius: 14,
                          backgroundColor: Colors.orange.shade100,
                          child: Text(
                            '${item.quantity}',
                            style: TextStyle(
                              fontSize: 12,
                              fontWeight: FontWeight.w700,
                              color: Colors.orange.shade900,
                            ),
                          ),
                        ),
                        title: Text(item.itemName),
                        trailing: item.unitPrice != null
                            ? Text('${item.unitPrice!.toStringAsFixed(2)} TL')
                            : null,
                      ),
                    ),
                  ],
                  const SizedBox(height: 16),
                  Container(
                    width: double.infinity,
                    padding: const EdgeInsets.all(14),
                    decoration: BoxDecoration(
                      color: Colors.grey.shade50,
                      borderRadius: BorderRadius.circular(14),
                      border: Border.all(color: Colors.grey.shade300),
                    ),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        const Text(
                          'Ham OCR metni',
                          style: TextStyle(fontWeight: FontWeight.w700),
                        ),
                        const SizedBox(height: 8),
                        SelectableText(
                          parsedOrder.rawOcrText,
                          style: TextStyle(
                            color: Colors.grey.shade700,
                            height: 1.4,
                          ),
                        ),
                      ],
                    ),
                  ),
                ],
              ),
            ),
          ),
          if (errorMessage != null) ...[
            const SizedBox(height: 12),
            Container(
              padding: const EdgeInsets.all(14),
              decoration: BoxDecoration(
                color: Colors.red.shade50,
                borderRadius: BorderRadius.circular(14),
                border: Border.all(color: Colors.red.shade100),
              ),
              child: Text(
                errorMessage,
                style: TextStyle(color: Colors.red.shade700),
              ),
            ),
          ],
          const SizedBox(height: 16),
          FilledButton.icon(
            onPressed: isConfirming ? null : () => _confirmOrder(parsedOrder),
            icon: isConfirming
                ? const SizedBox(
                    width: 18,
                    height: 18,
                    child: CircularProgressIndicator(strokeWidth: 2),
                  )
                : const Icon(Icons.save_outlined),
            label: Text(
              isConfirming
                  ? 'Kaydediliyor...'
                  : 'Bilgileri Onayla ve Kaydet',
            ),
            style: FilledButton.styleFrom(
              backgroundColor: Colors.green.shade600,
              foregroundColor: Colors.white,
              padding: const EdgeInsets.symmetric(vertical: 16),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildSuccessView(OrderConfirmResponse response) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        const SizedBox(height: 24),
        Icon(
          Icons.check_circle,
          color: Colors.green.shade600,
          size: 82,
        ),
        const SizedBox(height: 16),
        Text(
          'Sipariş kaydedildi',
          textAlign: TextAlign.center,
          style: TextStyle(
            fontSize: 26,
            fontWeight: FontWeight.w800,
            color: Colors.green.shade700,
          ),
        ),
        const SizedBox(height: 8),
        Text(
          'OCR taslağını onayladıktan sonra sipariş başarıyla veritabanına yazıldı.',
          textAlign: TextAlign.center,
          style: TextStyle(color: Colors.grey.shade700),
        ),
        const SizedBox(height: 24),
        Card(
          child: Padding(
            padding: const EdgeInsets.all(18),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                _SummaryRow(
                  icon: Icons.tag,
                  label: 'Sipariş ID',
                  value: response.orderId,
                ),
                if (response.restaurantName != null)
                  _SummaryRow(
                    icon: Icons.storefront_outlined,
                    label: 'Restoran',
                    value: response.restaurantName!,
                  ),
                if (response.totalAmount != null)
                  _SummaryRow(
                    icon: Icons.payments_outlined,
                    label: 'Tutar',
                    value: '${response.totalAmount!.toStringAsFixed(2)} TL',
                  ),
                if (response.foodContent != null && response.foodContent!.isNotEmpty)
                  _SummaryRow(
                    icon: Icons.fastfood_outlined,
                    label: 'İçerik',
                    value: response.foodContent!,
                  ),
              ],
            ),
          ),
        ),
        const SizedBox(height: 16),
        OutlinedButton.icon(
          onPressed: _startNewFlow,
          icon: const Icon(Icons.add_photo_alternate_outlined),
          label: const Text('Yeni fiş okut'),
        ),
        const SizedBox(height: 12),
        FilledButton.icon(
          onPressed: () => context.pushNamed(AppRoutes.orderHistoryName),
          icon: const Icon(Icons.history),
          label: const Text('Sipariş geçmişine git'),
          style: FilledButton.styleFrom(
            backgroundColor: Colors.orange,
            foregroundColor: Colors.white,
            padding: const EdgeInsets.symmetric(vertical: 16),
          ),
        ),
      ],
    );
  }

  Widget _buildThumbnailRow() {
    return Row(
      children: List.generate(_selectedImages.length, (index) {
        return Expanded(
          child: Padding(
            padding: EdgeInsets.only(
              right: index < _selectedImages.length - 1 ? 8 : 0,
            ),
            child: Stack(
              children: [
                ClipRRect(
                  borderRadius: BorderRadius.circular(14),
                  child: AspectRatio(
                    aspectRatio: 3 / 4,
                    child: Image.file(
                      File(_selectedImages[index]),
                      fit: BoxFit.cover,
                    ),
                  ),
                ),
                Positioned(
                  top: 6,
                  right: 6,
                  child: GestureDetector(
                    onTap: () => _removeImage(index),
                    child: Container(
                      decoration: BoxDecoration(
                        color: Colors.black.withValues(alpha: 0.65),
                        shape: BoxShape.circle,
                      ),
                      padding: const EdgeInsets.all(4),
                      child: const Icon(
                        Icons.close,
                        color: Colors.white,
                        size: 18,
                      ),
                    ),
                  ),
                ),
                Positioned(
                  bottom: 6,
                  left: 6,
                  child: Container(
                    padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
                    decoration: BoxDecoration(
                      color: Colors.black.withValues(alpha: 0.65),
                      borderRadius: BorderRadius.circular(8),
                    ),
                    child: Text(
                      '${index + 1}/$_maxImages',
                      style: const TextStyle(color: Colors.white, fontSize: 11),
                    ),
                  ),
                ),
              ],
            ),
          ),
        );
      }),
    );
  }
}

class _LoadingCard extends StatelessWidget {
  final String title;
  final String subtitle;

  const _LoadingCard({required this.title, required this.subtitle});

  @override
  Widget build(BuildContext context) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(18),
        child: Row(
          children: [
            const CircularProgressIndicator(),
            const SizedBox(width: 16),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    title,
                    style: const TextStyle(fontWeight: FontWeight.w700),
                  ),
                  const SizedBox(height: 4),
                  Text(subtitle),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }
}

class _InfoChip extends StatelessWidget {
  final IconData icon;
  final String label;

  const _InfoChip({required this.icon, required this.label});

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 8),
      decoration: BoxDecoration(
        color: Colors.grey.shade100,
        borderRadius: BorderRadius.circular(999),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(icon, size: 16, color: Colors.grey.shade700),
          const SizedBox(width: 6),
          Text(label),
        ],
      ),
    );
  }
}

class _SummaryRow extends StatelessWidget {
  final IconData icon;
  final String label;
  final String value;

  const _SummaryRow({
    required this.icon,
    required this.label,
    required this.value,
  });

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 12),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Icon(icon, size: 18, color: Colors.grey.shade700),
          const SizedBox(width: 8),
          SizedBox(
            width: 80,
            child: Text(
              label,
              style: TextStyle(
                fontWeight: FontWeight.w600,
                color: Colors.grey.shade700,
              ),
            ),
          ),
          Expanded(child: Text(value)),
        ],
      ),
    );
  }
}
