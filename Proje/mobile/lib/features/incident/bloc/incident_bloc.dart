import 'package:equatable/equatable.dart';
import 'package:flutter_bloc/flutter_bloc.dart';

import '../../../core/api/models/order_models.dart';
import '../../../core/api/services/incident_api_service.dart';
import '../../../core/api/services/order_api_service.dart';

part 'incident_event.dart';
part 'incident_state.dart';

class IncidentBloc extends Bloc<IncidentEvent, IncidentState> {
  final IncidentApiService _incidentApi;
  final OrderApiService _orderApi;

  IncidentBloc({
    IncidentApiService? incidentApi,
    OrderApiService? orderApi,
  })  : _incidentApi = incidentApi ?? IncidentApiService(),
        _orderApi = orderApi ?? OrderApiService(),
        super(const IncidentState()) {
    on<IncidentOrdersRequested>(_onIncidentOrdersRequested);
    on<IncidentReportSubmitted>(_onIncidentReportSubmitted);
    on<IncidentListRequested>(_onIncidentListRequested);
    on<IncidentReportStatusResetRequested>(_onIncidentReportStatusResetRequested);
  }

  Future<void> _onIncidentOrdersRequested(
    IncidentOrdersRequested event,
    Emitter<IncidentState> emit,
  ) async {
    emit(state.copyWith(
      ordersStatus: IncidentRequestStatus.loading,
      clearOrdersError: true,
    ));

    try {
      final res = await _orderApi.getMyHistory(page: event.page, limit: event.limit);
      emit(state.copyWith(
        ordersStatus: IncidentRequestStatus.success,
        orders: res.items,
        clearOrdersError: true,
      ));
    } catch (e) {
      emit(state.copyWith(
        ordersStatus: IncidentRequestStatus.failure,
        ordersError: _mapError(e),
      ));
    }
  }

  Future<void> _onIncidentReportSubmitted(
    IncidentReportSubmitted event,
    Emitter<IncidentState> emit,
  ) async {
    emit(state.copyWith(
      submitStatus: IncidentRequestStatus.loading,
      clearSubmitError: true,
      clearSubmitResponse: true,
    ));

    try {
      final res = await _incidentApi.reportIncident(
        suspectedOrderId: event.suspectedOrderId,
        symptoms: event.symptoms,
        severityLevel: event.severityLevel,
        isVerifiedByDoctor: event.isVerifiedByDoctor,
      );
      emit(state.copyWith(
        submitStatus: IncidentRequestStatus.success,
        submitResponse: res,
        clearSubmitError: true,
      ));
    } catch (e) {
      emit(state.copyWith(
        submitStatus: IncidentRequestStatus.failure,
        submitError: _mapError(e),
      ));
    }
  }

  Future<void> _onIncidentListRequested(
    IncidentListRequested event,
    Emitter<IncidentState> emit,
  ) async {
    emit(state.copyWith(
      incidentsStatus: IncidentRequestStatus.loading,
      clearIncidentsError: true,
    ));

    try {
      final res = await _incidentApi.getMyIncidents(page: event.page, limit: event.limit);
      emit(state.copyWith(
        incidentsStatus: IncidentRequestStatus.success,
        incidents: res.items,
        clearIncidentsError: true,
      ));
    } catch (e) {
      emit(state.copyWith(
        incidentsStatus: IncidentRequestStatus.failure,
        incidentsError: _mapError(e),
      ));
    }
  }

  void _onIncidentReportStatusResetRequested(
    IncidentReportStatusResetRequested event,
    Emitter<IncidentState> emit,
  ) {
    emit(state.copyWith(
      submitStatus: IncidentRequestStatus.initial,
      clearSubmitError: true,
      clearSubmitResponse: true,
    ));
  }

  String _mapError(Object error) {
    return error.toString().replaceFirst('Exception: ', '');
  }
}
