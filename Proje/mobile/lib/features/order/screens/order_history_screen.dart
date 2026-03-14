import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:intl/intl.dart';

import '../../../core/api/models/order_models.dart';
import '../bloc/order_bloc.dart';
import '../bloc/order_event.dart';
import '../bloc/order_state.dart';

/// Order history (sipariş geçmişi) - GET /v1/orders/my-history
/// TASK-MB-013: Liste, pagination, pull-to-refresh, empty state, date filter
class OrderHistoryScreen extends StatelessWidget {
  const OrderHistoryScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return BlocProvider(
      create: (_) => OrderBloc(),
      child: const _OrderHistoryView(),
    );
  }
}

class _OrderHistoryView extends StatefulWidget {
  const _OrderHistoryView();

  @override
  State<_OrderHistoryView> createState() => _OrderHistoryViewState();
}

class _OrderHistoryViewState extends State<_OrderHistoryView> {

  /// 0: Tümü, 1: Son 7 gün, 2: Son 30 gün
  int _dateFilterIndex = 0;

  DateTime? get _startDate {
    final now = DateTime.now();
    if (_dateFilterIndex == 1) return now.subtract(const Duration(days: 7));
    if (_dateFilterIndex == 2) return now.subtract(const Duration(days: 30));
    return null;
  }

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      _load(refresh: true);
    });
  }

  void _load({required bool refresh, int? page}) {
    final bloc = context.read<OrderBloc>();
    final nextPage = page ?? (refresh ? 1 : bloc.state.page + 1);
    bloc.add(
      OrderHistoryRequested(
        page: nextPage,
        limit: 20,
        startDate: _startDate,
        refresh: refresh,
      ),
    );
  }

  Future<void> _refresh() async {
    _load(refresh: true);
  }

  void _setDateFilter(int index) {
    if (_dateFilterIndex == index) return;
    setState(() {
      _dateFilterIndex = index;
    });
    _load(refresh: true, page: 1);
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Sipariş Geçmişi'),
        backgroundColor: Colors.orange,
        foregroundColor: Colors.white,
      ),
      body: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          _buildDateFilterChips(),
          Expanded(
            child: BlocBuilder<OrderBloc, OrderState>(
              builder: (context, state) {
                if (state.historyError != null && state.historyItems.isEmpty) {
                  return _buildErrorState(state.historyError!);
                }

                if (state.isHistoryLoading && state.historyItems.isEmpty) {
                  return const Center(child: CircularProgressIndicator());
                }

                if (state.historyItems.isEmpty) {
                  return _buildEmptyState();
                }

                return _buildList(state);
              },
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildDateFilterChips() {
    const labels = ['Tümü', 'Son 7 gün', 'Son 30 gün'];
    return SingleChildScrollView(
      scrollDirection: Axis.horizontal,
      padding: const EdgeInsets.fromLTRB(16, 12, 16, 8),
      child: Row(
        children: List.generate(3, (i) {
          final selected = _dateFilterIndex == i;
          return Padding(
            padding: const EdgeInsets.only(right: 8),
            child: FilterChip(
              label: Text(labels[i]),
              selected: selected,
              onSelected: (_) => _setDateFilter(i),
              selectedColor: Colors.orange.withValues(alpha: 0.3),
              checkmarkColor: Colors.orange,
            ),
          );
        }),
      ),
    );
  }

  Widget _buildErrorState(String errorMessage) {
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(24.0),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Icon(Icons.error_outline, size: 48, color: Colors.red[700]),
            const SizedBox(height: 16),
            Text(
              errorMessage,
              style: TextStyle(color: Colors.red[700], fontSize: 14),
              textAlign: TextAlign.center,
            ),
            const SizedBox(height: 16),
            FilledButton.icon(
              onPressed: () => _load(refresh: true, page: 1),
              icon: const Icon(Icons.refresh),
              label: const Text('Tekrar dene'),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildEmptyState() {
    return Center(
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(
            Icons.receipt_long_outlined,
            size: 64,
            color: Colors.grey[400],
          ),
          const SizedBox(height: 16),
          Text(
            'Henüz sipariş yok.',
            style: TextStyle(
              fontSize: 16,
              color: Colors.grey[600],
            ),
          ),
          if (_dateFilterIndex != 0) ...[
            const SizedBox(height: 8),
            Text(
              'Tarih filtresini değiştirmeyi deneyin.',
              style: TextStyle(fontSize: 12, color: Colors.grey[500]),
            ),
          ],
        ],
      ),
    );
  }

  Widget _buildList(OrderState state) {
    return RefreshIndicator(
      onRefresh: _refresh,
      child: ListView.builder(
        padding: const EdgeInsets.fromLTRB(16, 0, 16, 24),
        itemCount: state.historyItems.length + (state.hasMore ? 1 : 0),
        itemBuilder: (context, index) {
          if (index == state.historyItems.length) {
            if (state.hasMore && !state.isHistoryLoading) {
              _load(refresh: false);
            }
            return const Padding(
              padding: EdgeInsets.all(16.0),
              child: Center(child: CircularProgressIndicator()),
            );
          }
          return _OrderHistoryCard(order: state.historyItems[index]);
        },
      ),
    );
  }
}

class _OrderHistoryCard extends StatelessWidget {
  final OrderHistoryEntry order;

  const _OrderHistoryCard({required this.order});

  @override
  Widget build(BuildContext context) {
    final rest = order.restaurant;
    final name = rest?.name ?? 'Restoran bilinmiyor';
    final dateStr = DateFormat('d.M.y HH:mm').format(order.declaredAt);
    final amount = order.totalAmount != null
        ? '${order.totalAmount!.toStringAsFixed(2)} ₺'
        : '—';

    return Card(
      margin: const EdgeInsets.only(bottom: 12),
      elevation: 1,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Expanded(
                  child: Text(
                    name,
                    style: const TextStyle(
                      fontWeight: FontWeight.w600,
                      fontSize: 16,
                    ),
                  ),
                ),
                if (rest != null) _RiskBadge(status: rest.currentRiskStatus),
              ],
            ),
            // Sipariş İçeriği (food_content)
            if (order.foodContent != null && order.foodContent!.isNotEmpty) ...[
              const SizedBox(height: 6),
              Row(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Icon(Icons.restaurant_menu, size: 14, color: Colors.grey[500]),
                  const SizedBox(width: 6),
                  Expanded(
                    child: Text(
                      order.foodContent!,
                      style: TextStyle(
                        fontSize: 13,
                        color: Colors.grey[600],
                        fontStyle: FontStyle.italic,
                      ),
                      maxLines: 2,
                      overflow: TextOverflow.ellipsis,
                    ),
                  ),
                ],
              ),
            ],
            const SizedBox(height: 8),
            Row(
              children: [
                Icon(Icons.calendar_today, size: 14, color: Colors.grey[600]),
                const SizedBox(width: 6),
                Text(
                  dateStr,
                  style: TextStyle(fontSize: 13, color: Colors.grey[700]),
                ),
              ],
            ),
            const SizedBox(height: 4),
            Row(
              children: [
                Icon(Icons.receipt, size: 14, color: Colors.grey[600]),
                const SizedBox(width: 6),
                Text(
                  amount,
                  style: TextStyle(
                    fontSize: 14,
                    fontWeight: FontWeight.w500,
                    color: Colors.grey[800],
                  ),
                ),
                const SizedBox(width: 8),
                _MethodChip(method: order.method),
              ],
            ),
          ],
        ),
      ),
    );
  }
}

class _RiskBadge extends StatelessWidget {
  final String status;

  const _RiskBadge({required this.status});

  @override
  Widget build(BuildContext context) {
    Color color = Colors.grey;
    String label = status;
    if (status == 'RED_FLAG' || status == 'BLACKLISTED') {
      color = Colors.red;
      if (status == 'RED_FLAG') label = 'Riskli';
      if (status == 'BLACKLISTED') label = 'Yasaklı';
    } else if (status == 'WATCHLIST') {
      color = Colors.orange;
      label = 'İzlemede';
    } else {
      label = 'Güvenli';
      color = Colors.green;
    }
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
      decoration: BoxDecoration(
        color: color.withValues(alpha: 0.15),
        borderRadius: BorderRadius.circular(8),
        border: Border.all(color: color.withValues(alpha: 0.5)),
      ),
      child: Text(
        label,
        style: TextStyle(
          fontSize: 11,
          color: color,
          fontWeight: FontWeight.w600,
        ),
      ),
    );
  }
}

class _MethodChip extends StatelessWidget {
  final String method;

  const _MethodChip({required this.method});

  @override
  Widget build(BuildContext context) {
    final isReceipt = method.toUpperCase().contains('RECEIPT') ||
        method == 'fiş' ||
        method == 'fis';
    final label = isReceipt ? 'Fiş' : 'Ekran görüntüsü';
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
      decoration: BoxDecoration(
        color: Colors.blue.withValues(alpha: 0.1),
        borderRadius: BorderRadius.circular(6),
      ),
      child: Text(
        label,
        style: TextStyle(fontSize: 11, color: Colors.blue[700]),
      ),
    );
  }
}
