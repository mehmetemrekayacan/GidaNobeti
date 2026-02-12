import 'package:flutter/material.dart';
import 'package:image_picker/image_picker.dart';
import '../../../core/api/services/order_api_service.dart';
import '../../../core/api/models/order_models.dart';
import '../widgets/risk_warning_dialog.dart';

/// Order upload - fiş fotoğrafı yükle (POST /v1/orders/upload)
class OrderUploadScreen extends StatefulWidget {
  const OrderUploadScreen({super.key});

  @override
  State<OrderUploadScreen> createState() => _OrderUploadScreenState();
}

class _OrderUploadScreenState extends State<OrderUploadScreen> {
  final OrderApiService _api = OrderApiService();
  final ImagePicker _picker = ImagePicker();
  bool _uploading = false;
  String? _error;
  OrderUploadResponse? _result;

  Future<void> _pickAndUpload() async {
    try {
      final XFile? file = await _picker.pickImage(
        source: ImageSource.camera,
        maxWidth: 1280,
        imageQuality: 80,
      );
      if (file == null) return;
      final path = file.path;
      if (path == null || path.isEmpty) {
        setState(() => _error = 'Dosya yolu alınamadı');
        return;
      }
      setState(() {
        _uploading = true;
        _error = null;
        _result = null;
      });
      final res = await _api.uploadReceipt(path);
      if (mounted) {
        setState(() {
          _uploading = false;
          _result = res;
        });
        // Risk uyarısı varsa dialog göster
        _checkAndShowRiskWarning(res);
      }
    } catch (e) {
      if (mounted) {
        setState(() {
          _uploading = false;
          _error = e.toString().replaceFirst('Exception: ', '');
        });
      }
    }
  }

  Future<void> _pickFromGallery() async {
    try {
      final XFile? file = await _picker.pickImage(
        source: ImageSource.gallery,
        maxWidth: 1280,
        imageQuality: 80,
      );
      if (file == null) return;
      final path = file.path;
      if (path == null || path.isEmpty) {
        setState(() => _error = 'Dosya yolu alınamadı');
        return;
      }
      setState(() {
        _uploading = true;
        _error = null;
        _result = null;
      });
      final res = await _api.uploadReceipt(path);
      if (mounted) {
        setState(() {
          _uploading = false;
          _result = res;
        });
        // Risk uyarısı varsa dialog göster
        _checkAndShowRiskWarning(res);
      }
    } catch (e) {
      if (mounted) {
        setState(() {
          _uploading = false;
          _error = e.toString().replaceFirst('Exception: ', '');
        });
      }
    }
  }

  void _checkAndShowRiskWarning(OrderUploadResponse response) {
    // Backend'den gelen warning mesajı formatı: "Dikkat: {restaurant.name} riskli restoran listesinde!"
    final riskWarning = response.warnings.firstWhere(
      (w) => w.contains('riskli restoran') || w.contains('Dikkat'),
      orElse: () => '',
    );
    if (riskWarning.isNotEmpty) {
      // Restaurant name'i çıkar: "Dikkat: Restoran Adı riskli restoran listesinde!"
      String restaurantName = response.restaurantName ?? 'Bilinmeyen Restoran';
      final match = RegExp(r'Dikkat:\s*(.+?)\s*riskli').firstMatch(riskWarning);
      if (match != null) {
        restaurantName = match.group(1) ?? restaurantName;
      }
      WidgetsBinding.instance.addPostFrameCallback((_) {
        if (mounted) {
          RiskWarningDialog.show(
            context,
            restaurantName: restaurantName,
            riskReason: riskWarning,
          );
        }
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Sipariş Yükle'),
        backgroundColor: Colors.orange,
        foregroundColor: Colors.white,
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(24),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            const Text(
              'Fiş veya ekran görüntüsü yükleyin. OCR ile otomatik okunacak.',
              style: TextStyle(fontSize: 14, color: Colors.grey),
              textAlign: TextAlign.center,
            ),
            const SizedBox(height: 24),
            if (_uploading)
              const Center(
                child: Padding(
                  padding: EdgeInsets.all(32.0),
                  child: Column(
                    children: [
                      CircularProgressIndicator(),
                      SizedBox(height: 16),
                      Text('Yükleniyor ve işleniyor...'),
                    ],
                  ),
                ),
              )
            else ...[
              OutlinedButton.icon(
                onPressed: _pickAndUpload,
                icon: const Icon(Icons.camera_alt),
                label: const Text('Kamera ile çek'),
                style: OutlinedButton.styleFrom(
                  padding: const EdgeInsets.symmetric(vertical: 16),
                  foregroundColor: Colors.orange,
                ),
              ),
              const SizedBox(height: 12),
              OutlinedButton.icon(
                onPressed: _pickFromGallery,
                icon: const Icon(Icons.photo_library),
                label: const Text('Galeriden seç'),
                style: OutlinedButton.styleFrom(
                  padding: const EdgeInsets.symmetric(vertical: 16),
                  foregroundColor: Colors.orange,
                ),
              ),
            ],
            if (_error != null) ...[
              const SizedBox(height: 24),
              Card(
                color: Colors.red.shade50,
                child: Padding(
                  padding: const EdgeInsets.all(16.0),
                  child: Text(
                    _error!,
                    style: TextStyle(color: Colors.red.shade800),
                  ),
                ),
              ),
            ],
            if (_result != null) ...[
              const SizedBox(height: 24),
              Card(
                color: Colors.green.shade50,
                child: Padding(
                  padding: const EdgeInsets.all(16.0),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Row(
                        children: [
                          Icon(Icons.check_circle, color: Colors.green.shade700),
                          const SizedBox(width: 8),
                          Text(
                            'Sipariş kaydedildi',
                            style: TextStyle(
                              fontWeight: FontWeight.bold,
                              color: Colors.green.shade800,
                            ),
                          ),
                        ],
                      ),
                      if (_result!.restaurantName != null)
                        Padding(
                          padding: const EdgeInsets.only(top: 8),
                          child: Text('Restoran: ${_result!.restaurantName}'),
                        ),
                      if (_result!.totalAmount != null)
                        Padding(
                          padding: const EdgeInsets.only(top: 4),
                          child: Text(
                            'Tutar: ${_result!.totalAmount!.toStringAsFixed(2)} ₺',
                          ),
                        ),
                      if (_result!.warnings.isNotEmpty) ...[
                        const SizedBox(height: 12),
                        ..._result!.warnings.map(
                          (w) => Padding(
                            padding: const EdgeInsets.only(bottom: 4),
                            child: Row(
                              crossAxisAlignment: CrossAxisAlignment.start,
                              children: [
                                Icon(Icons.warning_amber,
                                    size: 18, color: Colors.orange.shade800),
                                const SizedBox(width: 8),
                                Expanded(
                                    child: Text(
                                  w,
                                  style: TextStyle(
                                      color: Colors.orange.shade900),
                                )),
                              ],
                            ),
                          ),
                        ),
                      ],
                    ],
                  ),
                ),
              ),
            ],
          ],
        ),
      ),
    );
  }
}
