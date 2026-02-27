import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:intl/intl.dart';
import '../../../core/api/models/order_models.dart';
import '../../../core/api/services/order_api_service.dart';
import '../../../core/api/services/incident_api_service.dart';
import '../../../core/router/app_routes.dart';

/// Sağlık sorunu bildirimi - TASK-MB-015
class IncidentReportScreen extends StatefulWidget {
  const IncidentReportScreen({super.key});

  @override
  State<IncidentReportScreen> createState() => _IncidentReportScreenState();
}

class _IncidentReportScreenState extends State<IncidentReportScreen> {
  final OrderApiService _orderApi = OrderApiService();
  final IncidentApiService _incidentApi = IncidentApiService();
  final _formKey = GlobalKey<FormState>();

  List<OrderHistoryEntry> _orders = [];
  bool _loadingOrders = true;
  String? _orderError;

  String? _selectedOrderId;
  final _symptomsController = TextEditingController();
  String? _selectedSeverity;
  bool _isDoctorVerified = false;
  bool _submitting = false;
  String? _submitError;
  bool _success = false;
  List<String> _nextSteps = [];

  static const Map<String, int> _severityToValue = {
    'Hafif': 1,
    'Orta': 3,
    'Ağır': 5,
  };

  @override
  void initState() {
    super.initState();
    _loadOrders();
  }

  @override
  void dispose() {
    _symptomsController.dispose();
    super.dispose();
  }

  Future<void> _loadOrders() async {
    setState(() {
      _loadingOrders = true;
      _orderError = null;
    });
    try {
      final res = await _orderApi.getMyHistory(page: 1, limit: 30);
      if (mounted) {
        setState(() {
          _orders = res.items;
          _loadingOrders = false;
          _selectedSeverity ??= 'Orta';
          if (_orders.isNotEmpty && _selectedOrderId == null) {
            _selectedOrderId = _orders.first.id;
          }
        });
      }
    } catch (e) {
      if (mounted) {
        setState(() {
          _orderError = e.toString().replaceFirst('Exception: ', '');
          _loadingOrders = false;
          _selectedSeverity ??= 'Orta';
        });
      }
    }
  }

  void _showSuccessDialog(String incidentId, List<String> nextSteps) {
    showDialog(
      context: context,
      barrierDismissible: true,
      builder: (ctx) => AlertDialog(
        title: const Row(
          children: [
            Icon(Icons.check_circle, color: Colors.green, size: 28),
            SizedBox(width: 8),
            Text('Bildirim alındı'),
          ],
        ),
        content: SingleChildScrollView(
          child: Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                'Kayıt no: $incidentId',
                style: TextStyle(
                  fontSize: 12,
                  color: Colors.grey[600],
                ),
              ),
              if (nextSteps.isNotEmpty) ...[
                const SizedBox(height: 12),
                const Text(
                  'Önerilen adımlar:',
                  style: TextStyle(
                    fontWeight: FontWeight.w600,
                    fontSize: 14,
                  ),
                ),
                const SizedBox(height: 6),
                ...nextSteps.map((s) => Padding(
                      padding: const EdgeInsets.only(bottom: 4),
                      child: Row(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text('• ', style: TextStyle(color: Colors.grey[700])),
                          Expanded(child: Text(s)),
                        ],
                      ),
                    )),
              ],
              const SizedBox(height: 12),
              Text(
                'Lütfen sağlık görevlisine de başvurunuz.',
                style: TextStyle(
                  fontWeight: FontWeight.w500,
                  color: Colors.orange[800],
                  fontSize: 13,
                ),
              ),
            ],
          ),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(ctx).pop(),
            child: const Text('Tamam'),
          ),
        ],
      ),
    ).then((_) {
      if (mounted) {
        setState(() {
          _success = false;
          _nextSteps = [];
          _symptomsController.clear();
          _submitError = null;
        });
      }
    });
  }

  Future<void> _submit() async {
    final isValid = _formKey.currentState?.validate() ?? false;
    if (!isValid) return;

    OrderHistoryEntry? order;
    for (final o in _orders) {
      if (o.id == _selectedOrderId) {
        order = o;
        break;
      }
    }

    final symptoms = _symptomsController.text.trim();
    final severityLabel = _selectedSeverity;
    final severityLevel =
        severityLabel == null ? null : _severityToValue[severityLabel];
    if (order == null || severityLevel == null) {
      setState(() {
        _submitError = 'Lütfen zorunlu alanları doldurun.';
      });
      return;
    }

    setState(() {
      _submitting = true;
      _submitError = null;
    });
    try {
      final res = await _incidentApi.reportIncident(
        suspectedOrderId: order.id,
        symptoms: symptoms,
        severityLevel: severityLevel,
        isVerifiedByDoctor: _isDoctorVerified,
      );
      if (mounted) {
        setState(() {
          _submitting = false;
          _success = true;
          _nextSteps = res.nextSteps;
        });
        WidgetsBinding.instance.addPostFrameCallback((_) {
          if (!mounted) return;
          _showSuccessDialog(res.incidentId, res.nextSteps);
        });
      }
    } catch (e) {
      if (mounted) {
        setState(() {
          _submitting = false;
          _submitError =
              e.toString().replaceFirst('Exception: ', '');
        });
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Sağlık Sorunu Bildir'),
        actions: [
          TextButton.icon(
            onPressed: () => context.pushNamed(AppRoutes.myIncidentsName),
            icon: const Icon(Icons.list_alt, size: 20, color: Colors.white),
            label: const Text('Bildirimlerim', style: TextStyle(color: Colors.white)),
          ),
        ],
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(20),
        child: Form(
          key: _formKey,
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
            Card(
              color: Theme.of(context).colorScheme.primaryContainer,
              child: const Padding(
                padding: EdgeInsets.all(16),
                child: Row(
                  children: [
                    Icon(Icons.info_outline),
                    SizedBox(width: 12),
                    Expanded(
                      child: Text(
                        'Bir siparişten sonra rahatsızlandıysanız bildirim yapabilirsiniz. Sağlık görevlisine de başvurunuz.',
                        style: TextStyle(fontSize: 13),
                      ),
                    ),
                  ],
                ),
              ),
            ),
            const SizedBox(height: 20),

            const Text(
              'Hangi siparişten şüpheleniliyor?',
              style: TextStyle(
                fontWeight: FontWeight.w600,
                fontSize: 14,
              ),
            ),
            const SizedBox(height: 8),
            if (_loadingOrders)
              const Row(
                children: [
                  SizedBox(
                    width: 18,
                    height: 18,
                    child: CircularProgressIndicator(strokeWidth: 2),
                  ),
                  SizedBox(width: 10),
                  Text('Siparişler yükleniyor...'),
                ],
              )
            else if (_orderError != null)
              Text(_orderError!, style: TextStyle(color: Colors.red[700]))
            else ...[
              DropdownButtonFormField<String>(
                value: _orders.isEmpty ? null : _selectedOrderId,
                decoration: const InputDecoration(
                  border: OutlineInputBorder(),
                  contentPadding:
                      EdgeInsets.symmetric(horizontal: 12, vertical: 12),
                ),
                items: _orders.map((o) {
                  final restaurantName = o.restaurant?.name ?? 'Restoran';
                  final orderDate = DateFormat('dd.MM.yyyy').format(o.declaredAt);
                  return DropdownMenuItem<String>(
                    value: o.id,
                    child: Text(
                      '$restaurantName - $orderDate',
                      overflow: TextOverflow.ellipsis,
                      maxLines: 1,
                    ),
                  );
                }).toList(),
                onChanged: _orders.isEmpty
                    ? null
                    : (v) {
                        setState(() {
                          _selectedOrderId = v;
                          _submitError = null;
                        });
                      },
                validator: (value) {
                  if (_orders.isEmpty) {
                    return null;
                  }
                  if (value == null || value.isEmpty) {
                    return 'Lütfen şüphelenilen siparişi seçin.';
                  }
                  return null;
                },
              ),
              if (_orders.isEmpty) ...[
                const SizedBox(height: 8),
                Text(
                  'Bildirim yapabilmek için en az bir geçmiş siparişiniz bulunmalıdır.',
                  style: TextStyle(
                    color: Theme.of(context).colorScheme.error,
                    fontSize: 13,
                  ),
                ),
              ],
            ],
            const SizedBox(height: 20),

            const Text(
              'Belirtiler (Semptomlar)',
              style: TextStyle(
                fontWeight: FontWeight.w600,
                fontSize: 14,
              ),
            ),
            const SizedBox(height: 8),
            TextFormField(
              controller: _symptomsController,
              keyboardType: TextInputType.multiline,
              textInputAction: TextInputAction.newline,
              maxLines: 4,
              maxLength: 2000,
              decoration: const InputDecoration(
                hintText: 'Örn: Mide bulantısı, baş ağrısı, kusma...',
                border: OutlineInputBorder(),
                alignLabelWithHint: true,
              ),
              onChanged: (_) => setState(() => _submitError = null),
              validator: (value) {
                final symptoms = (value ?? '').trim();
                if (symptoms.isEmpty) {
                  return 'Belirti alanı boş bırakılamaz.';
                }
                if (symptoms.length < 10) {
                  return 'Semptomları en az 10 karakter olacak şekilde yazın.';
                }
                if (symptoms.length > 2000) {
                  return 'Semptomlar en fazla 2000 karakter olabilir.';
                }
                return null;
              },
            ),
            const SizedBox(height: 20),

            const Text(
              'Şiddet Seviyesi',
              style: TextStyle(
                fontWeight: FontWeight.w600,
                fontSize: 14,
              ),
            ),
            const SizedBox(height: 8),
            DropdownButtonFormField<String>(
              value: _selectedSeverity,
              decoration: const InputDecoration(
                border: OutlineInputBorder(),
              ),
              items: _severityToValue.keys
                  .map(
                    (level) => DropdownMenuItem<String>(
                      value: level,
                      child: Text(level),
                    ),
                  )
                  .toList(),
              onChanged: (value) {
                setState(() {
                  _selectedSeverity = value;
                  _submitError = null;
                });
              },
              validator: (value) {
                if (value == null || value.isEmpty) {
                  return 'Lütfen şiddet seviyesi seçin.';
                }
                return null;
              },
            ),
            const SizedBox(height: 16),

            SwitchListTile.adaptive(
              contentPadding: const EdgeInsets.symmetric(horizontal: 4),
              title: const Text('Hastaneye gidildi / Doktor onaylı'),
              subtitle: const Text('Doktor tarafından doğrulandıysa işaretleyin'),
              value: _isDoctorVerified,
              onChanged: _submitting
                  ? null
                  : (value) => setState(() => _isDoctorVerified = value),
            ),

            const SizedBox(height: 24),

            if (_submitError != null) ...[
              Text(
                _submitError!,
                style: TextStyle(color: Colors.red[700], fontSize: 13),
              ),
              const SizedBox(height: 12),
            ],
            ElevatedButton(
              onPressed: _submitting
                  ? null
                  : _submit,
              style: ElevatedButton.styleFrom(
                padding: const EdgeInsets.symmetric(vertical: 16),
              ),
              child: _submitting
                  ? const SizedBox(
                      height: 24,
                      width: 24,
                      child: CircularProgressIndicator(
                        strokeWidth: 2,
                        color: Colors.white,
                      ),
                    )
                  : const Text('Bildir'),
            ),
            ],
          ),
        ),
      ),
    );
  }
}
