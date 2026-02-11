import 'package:flutter/material.dart';
import 'package:intl/intl.dart';
import '../../../core/api/models/order_models.dart';
import '../../../core/api/services/order_api_service.dart';
import '../../../core/api/services/incident_api_service.dart';

/// Sağlık sorunu bildirimi - TASK-MB-015
class IncidentReportScreen extends StatefulWidget {
  const IncidentReportScreen({super.key});

  @override
  State<IncidentReportScreen> createState() => _IncidentReportScreenState();
}

class _IncidentReportScreenState extends State<IncidentReportScreen> {
  final OrderApiService _orderApi = OrderApiService();
  final IncidentApiService _incidentApi = IncidentApiService();

  List<OrderHistoryEntry> _orders = [];
  bool _loadingOrders = true;
  String? _orderError;

  OrderHistoryEntry? _selectedOrder;
  final _symptomsController = TextEditingController();
  int _severity = 3;
  bool _submitting = false;
  String? _submitError;
  bool _success = false;
  List<String> _nextSteps = [];

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
      final now = DateTime.now();
      final threeDaysAgo = now.subtract(const Duration(days: 3));
      final recent = res.items
          .where((o) => o.declaredAt.isAfter(threeDaysAgo))
          .toList();
      if (mounted) {
        setState(() {
          _orders = recent;
          _loadingOrders = false;
          if (_orders.isNotEmpty && _selectedOrder == null) {
            _selectedOrder = _orders.first;
          }
        });
      }
    } catch (e) {
      if (mounted) {
        setState(() {
          _orderError = e.toString().replaceFirst('Exception: ', '');
          _loadingOrders = false;
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
    final order = _selectedOrder;
    final symptoms = _symptomsController.text.trim();
    if (order == null) {
      setState(() => _submitError = 'Lütfen şüphelenilen siparişi seçin.');
      return;
    }
    if (symptoms.length < 10) {
      setState(() =>
          _submitError = 'Semptomları en az 10 karakter olacak şekilde yazın.');
      return;
    }
    if (symptoms.length > 2000) {
      setState(() => _submitError = 'Semptomlar en fazla 2000 karakter olabilir.');
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
        severityLevel: _severity,
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
        backgroundColor: Colors.orange,
        foregroundColor: Colors.white,
        actions: [
          TextButton.icon(
            onPressed: () => Navigator.pushNamed(context, '/my-incidents'),
            icon: const Icon(Icons.list_alt, size: 20, color: Colors.white),
            label: const Text('Bildirimlerim', style: TextStyle(color: Colors.white)),
          ),
        ],
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(20),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            Card(
              color: Colors.blue.shade50,
              child: const Padding(
                padding: EdgeInsets.all(16),
                child: Row(
                  children: [
                    Icon(Icons.info_outline, color: Colors.blue),
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
              'Şüphelenilen sipariş (son 3 gün)',
              style: TextStyle(
                fontWeight: FontWeight.w600,
                fontSize: 14,
              ),
            ),
            const SizedBox(height: 8),
            if (_loadingOrders)
              const Center(
                  child: Padding(
                padding: EdgeInsets.all(24),
                child: CircularProgressIndicator(),
              ))
            else if (_orderError != null)
              Text(_orderError!, style: TextStyle(color: Colors.red[700]))
            else if (_orders.isEmpty)
              const Text(
                'Son 3 günde sipariş bulunamadı. Sipariş geçmişiniz boş olabilir.',
                style: TextStyle(color: Colors.grey),
              )
            else
              DropdownButtonFormField<OrderHistoryEntry>(
                value: _selectedOrder,
                decoration: const InputDecoration(
                  border: OutlineInputBorder(),
                  contentPadding:
                      EdgeInsets.symmetric(horizontal: 12, vertical: 12),
                ),
                items: _orders.map((o) {
                  final label =
                      '${o.restaurant?.name ?? "Restoran"} • ${DateFormat("d.M.y HH:mm").format(o.declaredAt)}';
                  return DropdownMenuItem(
                    value: o,
                    child: Text(
                      label,
                      overflow: TextOverflow.ellipsis,
                      maxLines: 1,
                    ),
                  );
                }).toList(),
                onChanged: (v) => setState(() => _selectedOrder = v),
              ),
            const SizedBox(height: 20),

            const Text(
              'Semptomlar (en az 10 karakter)',
              style: TextStyle(
                fontWeight: FontWeight.w600,
                fontSize: 14,
              ),
            ),
            const SizedBox(height: 8),
            TextField(
              controller: _symptomsController,
              maxLines: 4,
              maxLength: 2000,
              decoration: const InputDecoration(
                hintText: 'Örn: Mide bulantısı, baş ağrısı, kusma...',
                border: OutlineInputBorder(),
                alignLabelWithHint: true,
              ),
              onChanged: (_) => setState(() => _submitError = null),
            ),
            const SizedBox(height: 20),

            const Text(
              'Şiddet (1 = hafif, 5 = çok ciddi)',
              style: TextStyle(
                fontWeight: FontWeight.w600,
                fontSize: 14,
              ),
            ),
            const SizedBox(height: 8),
            Row(
              children: List.generate(5, (i) {
                final n = i + 1;
                final selected = _severity == n;
                return Expanded(
                  child: Padding(
                    padding: const EdgeInsets.symmetric(horizontal: 4),
                    child: Material(
                      color: selected ? Colors.orange : Colors.grey.shade200,
                      borderRadius: BorderRadius.circular(8),
                      child: InkWell(
                        onTap: () => setState(() => _severity = n),
                        borderRadius: BorderRadius.circular(8),
                        child: Center(
                          child: Padding(
                            padding: const EdgeInsets.symmetric(vertical: 12),
                            child: Text(
                              '$n',
                              style: TextStyle(
                                fontWeight: FontWeight.bold,
                                color: selected ? Colors.white : Colors.grey[700],
                              ),
                            ),
                          ),
                        ),
                      ),
                    ),
                  ),
                );
              }),
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
                backgroundColor: Colors.orange,
                foregroundColor: Colors.white,
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
    );
  }
}
