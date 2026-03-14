import 'package:equatable/equatable.dart';

import '../../../core/api/models/order_models.dart';

const Object _orderStateUnset = Object();

enum OrderStatus {
  initial,
  uploading,
  ocrSuccess,
  confirmed,
  error,
}

class OrderState extends Equatable {
  final OrderStatus status;
  final OrderParseResponse? parsedOrder;
  final OrderConfirmResponse? confirmedOrder;
  final String? errorMessage;
  final bool isHistoryLoading;
  final String? historyError;
  final List<OrderHistoryEntry> historyItems;
  final int page;
  final int limit;
  final int total;
  final bool hasMore;
  final DateTime? startDate;
  final DateTime? endDate;
  final int? restaurantId;

  const OrderState({
    this.status = OrderStatus.initial,
    this.parsedOrder,
    this.confirmedOrder,
    this.errorMessage,
    this.isHistoryLoading = false,
    this.historyError,
    this.historyItems = const [],
    this.page = 0,
    this.limit = 20,
    this.total = 0,
    this.hasMore = true,
    this.startDate,
    this.endDate,
    this.restaurantId,
  });

  bool get hasParsedOrder => parsedOrder != null;
  bool get hasConfirmedOrder => confirmedOrder != null;

  OrderState copyWith({
    OrderStatus? status,
    Object? parsedOrder = _orderStateUnset,
    Object? confirmedOrder = _orderStateUnset,
    Object? errorMessage = _orderStateUnset,
    bool? isHistoryLoading,
    Object? historyError = _orderStateUnset,
    List<OrderHistoryEntry>? historyItems,
    int? page,
    int? limit,
    int? total,
    bool? hasMore,
    Object? startDate = _orderStateUnset,
    Object? endDate = _orderStateUnset,
    Object? restaurantId = _orderStateUnset,
  }) {
    return OrderState(
      status: status ?? this.status,
      parsedOrder: identical(parsedOrder, _orderStateUnset)
          ? this.parsedOrder
          : parsedOrder as OrderParseResponse?,
      confirmedOrder: identical(confirmedOrder, _orderStateUnset)
          ? this.confirmedOrder
          : confirmedOrder as OrderConfirmResponse?,
      errorMessage: identical(errorMessage, _orderStateUnset)
          ? this.errorMessage
          : errorMessage as String?,
      isHistoryLoading: isHistoryLoading ?? this.isHistoryLoading,
      historyError: identical(historyError, _orderStateUnset)
          ? this.historyError
          : historyError as String?,
      historyItems: historyItems ?? this.historyItems,
      page: page ?? this.page,
      limit: limit ?? this.limit,
      total: total ?? this.total,
      hasMore: hasMore ?? this.hasMore,
      startDate: identical(startDate, _orderStateUnset)
          ? this.startDate
          : startDate as DateTime?,
      endDate: identical(endDate, _orderStateUnset)
          ? this.endDate
          : endDate as DateTime?,
      restaurantId: identical(restaurantId, _orderStateUnset)
          ? this.restaurantId
          : restaurantId as int?,
    );
  }

  @override
  List<Object?> get props => [
        status,
        parsedOrder,
        confirmedOrder,
        errorMessage,
        isHistoryLoading,
        historyError,
        historyItems,
        page,
        limit,
        total,
        hasMore,
        startDate,
        endDate,
        restaurantId,
      ];
}