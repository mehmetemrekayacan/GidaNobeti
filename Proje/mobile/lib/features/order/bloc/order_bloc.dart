import 'package:flutter_bloc/flutter_bloc.dart';

import '../../../core/api/services/order_api_service.dart';
import 'order_event.dart';
import 'order_state.dart';

class OrderBloc extends Bloc<OrderEvent, OrderState> {
  final OrderApiService _orderApi;

  OrderBloc({OrderApiService? orderApi})
      : _orderApi = orderApi ?? OrderApiService(),
        super(const OrderState()) {
    on<OrderHistoryRequested>(_onOrderHistoryRequested);
    on<OrderReceiptParseRequested>(_onOrderReceiptParseRequested);
    on<OrderConfirmationRequested>(_onOrderConfirmationRequested);
    on<OrderFlowResetRequested>(_onOrderFlowResetRequested);
  }

  Future<void> _onOrderHistoryRequested(
    OrderHistoryRequested event,
    Emitter<OrderState> emit,
  ) async {
    if (state.isHistoryLoading) return;

    emit(state.copyWith(
      isHistoryLoading: true,
      historyError: null,
      startDate: event.startDate,
      endDate: event.endDate,
      restaurantId: event.restaurantId,
      page: event.refresh ? 0 : state.page,
      hasMore: event.refresh ? true : state.hasMore,
      historyItems: event.refresh ? const [] : state.historyItems,
    ));

    try {
      final response = await _orderApi.getMyHistory(
        page: event.page,
        limit: event.limit,
        startDate: event.startDate,
        endDate: event.endDate,
        restaurantId: event.restaurantId,
      );

      final items = event.refresh || event.page == 1
          ? response.items
          : [...state.historyItems, ...response.items];

      emit(state.copyWith(
        isHistoryLoading: false,
        historyItems: items,
        page: response.page,
        limit: response.limit,
        total: response.total,
        hasMore: items.length < response.total,
        historyError: null,
      ));
    } catch (error) {
      emit(state.copyWith(
        isHistoryLoading: false,
        historyError: _mapError(error),
      ));
    }
  }

  Future<void> _onOrderReceiptParseRequested(
    OrderReceiptParseRequested event,
    Emitter<OrderState> emit,
  ) async {
    emit(state.copyWith(
      status: OrderStatus.uploading,
      errorMessage: null,
      parsedOrder: null,
      confirmedOrder: null,
    ));

    try {
      final response = await _orderApi.parseReceipts(event.filePaths);
      emit(state.copyWith(
        status: OrderStatus.ocrSuccess,
        parsedOrder: response,
        confirmedOrder: null,
        errorMessage: null,
      ));
    } catch (error) {
      emit(state.copyWith(
        status: OrderStatus.error,
        errorMessage: _mapError(error),
        parsedOrder: null,
        confirmedOrder: null,
      ));
    }
  }

  Future<void> _onOrderConfirmationRequested(
    OrderConfirmationRequested event,
    Emitter<OrderState> emit,
  ) async {
    final currentParsedOrder = state.parsedOrder;

    emit(state.copyWith(
      status: OrderStatus.uploading,
      errorMessage: null,
      confirmedOrder: null,
    ));

    try {
      final response = await _orderApi.confirmParsedOrder(event.request);
      emit(state.copyWith(
        status: OrderStatus.confirmed,
        parsedOrder: null,
        confirmedOrder: response,
        errorMessage: null,
      ));
    } catch (error) {
      emit(state.copyWith(
        status: OrderStatus.error,
        parsedOrder: currentParsedOrder,
        confirmedOrder: null,
        errorMessage: _mapError(error),
      ));
    }
  }

  void _onOrderFlowResetRequested(
    OrderFlowResetRequested event,
    Emitter<OrderState> emit,
  ) {
    emit(state.copyWith(
      status: OrderStatus.initial,
      parsedOrder: null,
      confirmedOrder: null,
      errorMessage: null,
    ));
  }

  String _mapError(Object error) {
    return error.toString().replaceFirst('Exception: ', '');
  }
}