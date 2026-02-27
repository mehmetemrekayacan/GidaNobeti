import 'package:dio/dio.dart';
import '../dio_client.dart';

/// Incident API - report + list my incidents (Bildirimlerim)
class IncidentApiService {
  final DioClient _client;

  IncidentApiService([DioClient? client]) : _client = client ?? DioClient();

  /// POST /v1/incidents/report
  Future<IncidentReportResponse> reportIncident({
    required String suspectedOrderId,
    required String symptoms,
    required int severityLevel,
    bool? isVerifiedByDoctor,
  }) async {
    final payload = <String, dynamic>{
      'suspected_order_id': suspectedOrderId,
      'symptoms': symptoms,
      'severity_level': severityLevel,
    };
    if (isVerifiedByDoctor != null) {
      payload['is_verified_by_doctor'] = isVerifiedByDoctor;
    }

    final response = await _client.post(
      '/v1/incidents/report',
      data: payload,
    );
    return IncidentReportResponse.fromJson(
        response.data as Map<String, dynamic>);
  }

  /// GET /v1/incidents/me - Öğrencinin kendi vaka listesi
  Future<MyIncidentListResponse> getMyIncidents({
    int page = 1,
    int limit = 20,
  }) async {
    final response = await _client.get(
      '/v1/incidents/me',
      queryParameters: {'page': page, 'limit': limit},
    );
    return MyIncidentListResponse.fromJson(
        response.data as Map<String, dynamic>);
  }
}

class IncidentReportResponse {
  final String incidentId;
  final List<String> nextSteps;

  IncidentReportResponse({
    required this.incidentId,
    this.nextSteps = const [],
  });

  factory IncidentReportResponse.fromJson(Map<String, dynamic> json) {
    final steps = json['next_steps'] as List<dynamic>? ?? [];
    return IncidentReportResponse(
      incidentId: json['incident_id'] as String,
      nextSteps: steps.map((e) => e as String).toList(),
    );
  }
}

/// Tek vaka satırı (Bildirimlerim listesi)
class MyIncidentListItem {
  final String id;
  final String? restaurantName;
  final String symptoms;
  final int? severityLevel;
  final String status;
  final DateTime reportDate;

  MyIncidentListItem({
    required this.id,
    this.restaurantName,
    required this.symptoms,
    this.severityLevel,
    required this.status,
    required this.reportDate,
  });

  factory MyIncidentListItem.fromJson(Map<String, dynamic> json) {
    return MyIncidentListItem(
      id: json['id'] as String,
      restaurantName: json['restaurant_name'] as String?,
      symptoms: json['symptoms'] as String,
      severityLevel: json['severity_level'] as int?,
      status: json['status'] as String,
      reportDate: DateTime.parse(json['report_date'] as String),
    );
  }
}

class MyIncidentListResponse {
  final int total;
  final int page;
  final int limit;
  final List<MyIncidentListItem> items;

  MyIncidentListResponse({
    required this.total,
    required this.page,
    required this.limit,
    required this.items,
  });

  factory MyIncidentListResponse.fromJson(Map<String, dynamic> json) {
    final itemsList = json['items'] as List<dynamic>? ?? [];
    return MyIncidentListResponse(
      total: json['total'] as int,
      page: json['page'] as int,
      limit: json['limit'] as int,
      items: itemsList
          .map((e) => MyIncidentListItem.fromJson(e as Map<String, dynamic>))
          .toList(),
    );
  }
}
