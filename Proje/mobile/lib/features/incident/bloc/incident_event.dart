part of 'incident_bloc.dart';

abstract class IncidentEvent extends Equatable {
  const IncidentEvent();

  @override
  List<Object?> get props => [];
}

class IncidentOrdersRequested extends IncidentEvent {
  final int page;
  final int limit;

  const IncidentOrdersRequested({
    this.page = 1,
    this.limit = 30,
  });

  @override
  List<Object?> get props => [page, limit];
}

class IncidentReportSubmitted extends IncidentEvent {
  final String suspectedOrderId;
  final String symptoms;
  final int severityLevel;
  final bool isVerifiedByDoctor;

  const IncidentReportSubmitted({
    required this.suspectedOrderId,
    required this.symptoms,
    required this.severityLevel,
    required this.isVerifiedByDoctor,
  });

  @override
  List<Object?> get props => [
        suspectedOrderId,
        symptoms,
        severityLevel,
        isVerifiedByDoctor,
      ];
}

class IncidentListRequested extends IncidentEvent {
  final int page;
  final int limit;

  const IncidentListRequested({
    this.page = 1,
    this.limit = 50,
  });

  @override
  List<Object?> get props => [page, limit];
}

class IncidentReportStatusResetRequested extends IncidentEvent {
  const IncidentReportStatusResetRequested();
}
