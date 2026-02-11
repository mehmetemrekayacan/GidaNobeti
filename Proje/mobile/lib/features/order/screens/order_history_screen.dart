import 'package:flutter/material.dart';
import 'package:intl/intl.dart';
import '../../../core/api/models/order_models.dart';
import '../../../core/api/services/order_api_service.dart';

/// Order history (sipariş geçmişi) - GET /v1/orders/my-history
class OrderHistoryScreen extends StatefulWidget {
  const OrderHistoryScreen({super.key});

  @override
  State<OrderHistoryScreen> createState() => _OrderHistoryScreenState();
}

class _OrderHistoryScreenState extends State<OrderHistoryScreen> {
  final OrderApiService _api = OrderApiService();
  int _page = 1;
  final List<OrderHistoryEntry> _items = [];
  bool _loading = false;
  bool _hasMore = true;
  String? _error;

  @override
  void initState() {
    super.initState();
    _loadMore();
  }

  Future<void> _loadMore() async {
    if (_loading || !_hasMore) return;
    setState(() {
      _loading = true;
      _error = null;
    });
    try {
      final res = await _api.getMyHistory(page: _page, limit: 20);
      setState(() {
        _items.addAll(res.items);
        _hasMore = res.items.length >= res.limit && _items.length < res.total;
        _page++;
        _loading = false;
      });
    } catch (e) {
      setState(() {
        _error = e.toString();
        _loading = false;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Sipariş Geçmişi'),
        backgroundColor: Colors.orange,
        foregroundColor: Colors.white,
      ),
      body: _error != null
          ? Center(
              child: Padding(
                padding: const EdgeInsets.all(24.0),
                child: Column(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    Text(
                      _error!,
                      style: TextStyle(color: Colors.red[700]),
                      textAlign: TextAlign.center,
                    ),
                    const SizedBox(height: 16),
                    TextButton(
                      onPressed: () {
                        setState(() {
                          _error = null;
                          _page = 1;
                          _items.clear();
                          _hasMore = true;
                        });
                        _loadMore();
                      },
                      child: const Text('Tekrar dene'),
                    ),
                  ],
                ),
              ),
            )
          : _items.isEmpty && _loading
              ? const Center(child: CircularProgressIndicator())
              : _items.isEmpty
                  ? const Center(child: Text('Henüz sipariş yok.'))
                  : RefreshIndicator(
                      onRefresh: () async {
                        setState(() {
                          _page = 1;
                          _items.clear();
                          _hasMore = true;
                        });
                        await _loadMore();
                      },
                      child: ListView.builder(
                        padding: const EdgeInsets.all(16),
                        itemCount: _items.length + (_hasMore ? 1 : 0),
                        itemBuilder: (context, index) {
                          if (index == _items.length) {
                            if (_hasMore && !_loading) _loadMore();
                            return const Padding(
                              padding: EdgeInsets.all(16.0),
                              child: Center(child: CircularProgressIndicator()),
                            );
                          }
                          final order = _items[index];
                          return Card(
                            margin: const EdgeInsets.only(bottom: 12),
                            child: ListTile(
                              title: Text(
                                order.restaurant?.name ?? 'Restoran bilinmiyor',
                              ),
                              subtitle: Text(
                                '${DateFormat('d.M.y HH:mm').format(order.declaredAt)}'
                                '${order.totalAmount != null ? ' • ${order.totalAmount!.toStringAsFixed(2)} ₺' : ''}',
                              ),
                              trailing: order.restaurant != null
                                  ? _riskChip(order.restaurant!.currentRiskStatus)
                                  : null,
                            ),
                          );
                        },
                      ),
                    ),
    );
  }

  Widget _riskChip(String status) {
    Color color = Colors.grey;
    if (status == 'RED_FLAG' || status == 'BLACKLISTED') color = Colors.red;
    if (status == 'WATCHLIST') color = Colors.orange;
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
      decoration: BoxDecoration(
        color: color.withValues(alpha: 0.2),
        borderRadius: BorderRadius.circular(8),
      ),
      child: Text(
        status,
        style: TextStyle(fontSize: 10, color: color, fontWeight: FontWeight.w600),
      ),
    );
  }
}
