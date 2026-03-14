import 'package:equatable/equatable.dart';

import '../../../core/api/models/order_models.dart';

abstract class OrderEvent extends Equatable {
  const OrderEvent();

  @override
  List<Object?> get props => [];
}

class OrderHistoryRequested extends OrderEvent {
  final int page;
  final int limit;
  final DateTime? startDate;
  final DateTime? endDate;
  final int? restaurantId;
  final bool refresh;

  const OrderHistoryRequested({
    required this.page,
    required this.limit,
    this.startDate,
    this.endDate,
    this.restaurantId,
    this.refresh = false,
  });

  @override
  List<Object?> get props => [page, limit, startDate, endDate, restaurantId, refresh];
}

class OrderReceiptParseRequested extends OrderEvent {
  final List<String> filePaths;

  const OrderReceiptParseRequested({required this.filePaths});

  @override
  List<Object?> get props => [filePaths];
}

class OrderConfirmationRequested extends OrderEvent {
  final OrderConfirmRequest request;

  const OrderConfirmationRequested({required this.request});

  @override
  List<Object?> get props => [request];
}

class OrderFlowResetRequested extends OrderEvent {
  const OrderFlowResetRequested();
}