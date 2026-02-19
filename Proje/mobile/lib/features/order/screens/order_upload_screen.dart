import 'dart:io';
import 'package:flutter/material.dart';
import 'package:image_picker/image_picker.dart';
import '../../../core/api/services/order_api_service.dart';
import '../../../core/api/models/order_models.dart';
import '../widgets/risk_warning_dialog.dart';

/// Order upload - fiş fotoğrafı yükle (POST /v1/orders/upload)
/// Tek veya çoklu (max 2) görsel destekler (Trendyol gibi uzun fişler için).
class OrderUploadScreen extends StatefulWidget {
  const OrderUploadScreen({super.key});

  @override
  State<OrderUploadScreen> createState() => _OrderUploadScreenState();
}

class _OrderUploadScreenState extends State<OrderUploadScreen> {
  final OrderApiService _api = OrderApiService();
  final ImagePicker _picker = ImagePicker();

  /// Seçilen görsellerin yol listesi (max 2)
  final List<String> _selectedImages = [];
  static const int _maxImages = 2;

  bool _uploading = false;
  String? _error;
  OrderUploadResponse? _result;

  // ── Görsel Ekleme ──────────────────────────────────────────────────────────

  Future<void> _pickFromCamera() async {
    if (_selectedImages.length >= _maxImages) {
      _showMaxImagesWarning();
      return;
    }
    try {
      final XFile? file = await _picker.pickImage(
        source: ImageSource.camera,
        maxWidth: 1280,
        imageQuality: 80,
      );
      if (file == null) return;
      final path = file.path;
      if (path.isEmpty) {
        setState(() => _error = 'Dosya yolu alınamadı');
        return;
      }
      setState(() {
        _selectedImages.add(path);
        _error = null;
        _result = null;
      });
    } catch (e) {
      if (mounted) {
        setState(
            () => _error = e.toString().replaceFirst('Exception: ', ''));
      }
    }
  }

  Future<void> _pickFromGallery() async {
    if (_selectedImages.length >= _maxImages) {
      _showMaxImagesWarning();
      return;
    }
    try {
      final remaining = _maxImages - _selectedImages.length;
      if (remaining > 1) {
        // Çoklu seçim
        final List<XFile> files = await _picker.pickMultiImage(
          maxWidth: 1280,
          imageQuality: 80,
        );
        if (files.isEmpty) return;
        final toAdd = files
            .take(remaining)
            .map((f) => f.path)
            .where((p) => p.isNotEmpty)
            .toList();
        if (toAdd.isEmpty) {
          setState(() => _error = 'Dosya yolu alınamadı');
          return;
        }
        setState(() {
          _selectedImages.addAll(toAdd);
          _error = null;
          _result = null;
        });
      } else {
        // Tek görsel kaldı
        final XFile? file = await _picker.pickImage(
          source: ImageSource.gallery,
          maxWidth: 1280,
          imageQuality: 80,
        );
        if (file == null) return;
        final path = file.path;
        if (path.isEmpty) {
          setState(() => _error = 'Dosya yolu alınamadı');
          return;
        }
        setState(() {
          _selectedImages.add(path);
          _error = null;
          _result = null;
        });
      }
    } catch (e) {
      if (mounted) {
        setState(
            () => _error = e.toString().replaceFirst('Exception: ', ''));
      }
    }
  }

  void _removeImage(int index) {
    setState(() {
      _selectedImages.removeAt(index);
      _result = null;
      _error = null;
    });
  }

  void _showMaxImagesWarning() {
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(
        content: Text('En fazla $_maxImages görsel seçebilirsiniz.'),
        duration: Duration(seconds: 2),
      ),
    );
  }

  // ── Yükleme ────────────────────────────────────────────────────────────────

  Future<void> _uploadImages() async {
    if (_selectedImages.isEmpty) return;

    setState(() {
      _uploading = true;
      _error = null;
      _result = null;
    });

    try {
      final res = await _api.uploadReceipts(_selectedImages);
      if (mounted) {
        setState(() {
          _uploading = false;
          _result = res;
        });
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
    if (response.warnings.isEmpty) return;

    String? riskWarning;
    for (final w in response.warnings) {
      if (w.contains('riskli restoran') || w.contains('Dikkat')) {
        riskWarning = w;
        break;
      }
    }

    if (riskWarning != null && riskWarning.isNotEmpty) {
      String restaurantName = response.restaurantName ?? 'Bilinmeyen Restoran';
      final match =
          RegExp(r'Dikkat:\s*(.+?)\s*riskli').firstMatch(riskWarning);
      if (match != null && match.group(1) != null) {
        restaurantName = match.group(1)!.trim();
      }

      WidgetsBinding.instance.addPostFrameCallback((_) {
        if (mounted) {
          try {
            RiskWarningDialog.show(
              context,
              restaurantName: restaurantName,
              riskReason: riskWarning,
            );
          } catch (e) {
            debugPrint('RiskWarningDialog gösterilirken hata: $e');
          }
        }
      });
    }
  }

  // ── UI ──────────────────────────────────────────────────────────────────────

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
              'Fiş veya ekran görüntüsü yükleyin. OCR ile otomatik okunacak.\n'
              'Uzun fişler için 2 görsel seçebilirsiniz.',
              style: TextStyle(fontSize: 14, color: Colors.grey),
              textAlign: TextAlign.center,
            ),
            const SizedBox(height: 24),

            // ── Seçilen Görseller Önizleme ─────────────────────────────────
            if (_selectedImages.isNotEmpty) ...[
              _buildThumbnailRow(),
              const SizedBox(height: 16),
            ],

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
              // Görsel ekleme butonları
              if (_selectedImages.length < _maxImages) ...[
                OutlinedButton.icon(
                  onPressed: _pickFromCamera,
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
                  label: Text(_selectedImages.isEmpty
                      ? 'Galeriden seç'
                      : 'Galeriden ekle'),
                  style: OutlinedButton.styleFrom(
                    padding: const EdgeInsets.symmetric(vertical: 16),
                    foregroundColor: Colors.orange,
                  ),
                ),
              ],

              // Yükle butonu
              if (_selectedImages.isNotEmpty) ...[
                const SizedBox(height: 16),
                ElevatedButton.icon(
                  onPressed: _uploadImages,
                  icon: const Icon(Icons.cloud_upload),
                  label: Text(
                    _selectedImages.length == 1
                        ? 'Yükle (1 görsel)'
                        : 'Yükle (${_selectedImages.length} görsel)',
                  ),
                  style: ElevatedButton.styleFrom(
                    padding: const EdgeInsets.symmetric(vertical: 16),
                    backgroundColor: Colors.orange,
                    foregroundColor: Colors.white,
                  ),
                ),
              ],
            ],

            // ── Hata Mesajı ────────────────────────────────────────────────
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

            // ── Sonuç Kartı ────────────────────────────────────────────────
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
                          Icon(Icons.check_circle,
                              color: Colors.green.shade700),
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
                          child:
                              Text('Restoran: ${_result!.restaurantName}'),
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
                                    size: 18,
                                    color: Colors.orange.shade800),
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

  /// Seçilen görselleri yan yana küçük önizlemeler olarak gösterir.
  /// Her birinin üzerinde çarpı (×) butonu ile kaldırılabilir.
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
                  borderRadius: BorderRadius.circular(12),
                  child: AspectRatio(
                    aspectRatio: 3 / 4,
                    child: Image.file(
                      File(_selectedImages[index]),
                      fit: BoxFit.cover,
                    ),
                  ),
                ),
                // Çarpı (×) butonu
                Positioned(
                  top: 4,
                  right: 4,
                  child: GestureDetector(
                    onTap: () => _removeImage(index),
                    child: Container(
                      decoration: BoxDecoration(
                        color: Colors.black.withOpacity(0.6),
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
                // Sayfa numarası
                Positioned(
                  bottom: 4,
                  left: 4,
                  child: Container(
                    padding:
                        const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
                    decoration: BoxDecoration(
                      color: Colors.black.withOpacity(0.6),
                      borderRadius: BorderRadius.circular(8),
                    ),
                    child: Text(
                      '${index + 1}/$_maxImages',
                      style: const TextStyle(
                          color: Colors.white, fontSize: 11),
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
