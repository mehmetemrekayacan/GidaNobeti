part of 'incident_bloc.dart';

enum IncidentRequestStatus {
  initial,
  loading,
  success,
  failure,
}

class IncidentState extends Equatable {
  final IncidentRequestStatus ordersStatus;
  final IncidentRequestStatus submitStatus;
  final IncidentRequestStatus incidentsStatus;
  final List<OrderHistoryEntry> orders;
  final List<MyIncidentListItem> incidents;
  final IncidentReportResponse? submitResponse;
  final String? ordersError;
  final String? submitError;
  final String? incidentsError;

  const IncidentState({
    this.ordersStatus = IncidentRequestStatus.initial,
    this.submitStatus = IncidentRequestStatus.initial,
    this.incidentsStatus = IncidentRequestStatus.initial,
    this.orders = const [],
    this.incidents = const [],
    this.submitResponse,
    this.ordersError,
    this.submitError,
    this.incidentsError,
  });

  IncidentState copyWith({
    IncidentRequestStatus? ordersStatus,
    IncidentRequestStatus? submitStatus,
    IncidentRequestStatus? incidentsStatus,
    List<OrderHistoryEntry>? orders,
    List<MyIncidentListItem>? incidents,
    IncidentReportResponse? submitResponse,
    String? ordersError,
    String? submitError,
    String? incidentsError,
    bool clearOrdersError = false,
    bool clearSubmitError = false,
    bool clearIncidentsError = false,
    bool clearSubmitResponse = false,
  }) {
    return IncidentState(
      ordersStatus: ordersStatus ?? this.ordersStatus,
      submitStatus: submitStatus ?? this.submitStatus,
      incidentsStatus: incidentsStatus ?? this.incidentsStatus,
      orders: orders ?? this.orders,
      incidents: incidents ?? this.incidents,
      submitResponse: clearSubmitResponse ? null : (submitResponse ?? this.submitResponse),
      ordersError: clearOrdersError ? null : (ordersError ?? this.ordersError),
      submitError: clearSubmitError ? null : (submitError ?? this.submitError),
      incidentsError: clearIncidentsError ? null : (incidentsError ?? this.incidentsError),
    );
  }

  @override
  List<Object?> get props => [
        ordersStatus,
        submitStatus,
        incidentsStatus,
        orders,
        incidents,
        submitResponse,
        ordersError,
        submitError,
        incidentsError,
      ];
}
