import 'package:dio/dio.dart';
import '../dio_client.dart';
import '../models/order_models.dart';

class OrderApiException implements Exception {
  final String message;
  final String? errorCode;

  const OrderApiException({required this.message, this.errorCode});

  @override
  String toString() => message;
}

/// Order API Service - parse/confirm receipt flow & order history
class OrderApiService {
  final DioClient _client;

  OrderApiService([DioClient? client]) : _client = client ?? DioClient();

  /// GET /v1/orders/my-history
  Future<OrderHistoryListResponse> getMyHistory({
    int page = 1,
    int limit = 20,
    DateTime? startDate,
    DateTime? endDate,
    int? restaurantId,
  }) async {
    final params = <String, dynamic>{'page': page, 'limit': limit};
    if (startDate != null) {
      params['start_date'] = startDate.toUtc().toIso8601String();
    }
    if (endDate != null) {
      params['end_date'] = endDate.toUtc().toIso8601String();
    }
    if (restaurantId != null) params['restaurant_id'] = restaurantId;
    final response = await _client.get(
      '/v1/orders/my-history',
      queryParameters: params,
    );
    return OrderHistoryListResponse.fromJson(
        response.data as Map<String, dynamic>);
  }

  /// POST /v1/orders/parse - parse single receipt image (backward compat)
  Future<OrderParseResponse> parseReceipt(String filePath) async {
    return parseReceipts([filePath]);
  }

  /// POST /v1/orders/parse - parse one or more receipt images.
  Future<OrderParseResponse> parseReceipts(List<String> filePaths) async {
    try {
      final response = await _client.postMultipartMultiple(
        '/v1/orders/parse',
        filePaths: filePaths,
        fieldName: 'files',
      );
      return OrderParseResponse.fromJson(
          response.data as Map<String, dynamic>);
    } on ClientException catch (e) {
      const readableCodes = {
        'OCR_UNREADABLE',
        'PARSER_RESTAURANT_NOT_FOUND',
        'PARSER_UNREADABLE',
      };

      if (e.statusCode == 400 && readableCodes.contains(e.errorCode)) {
        throw const OrderApiException(
          message:
              'Fiş okunamadı veya restoran tespit edilemedi, lütfen daha net bir fotoğraf çekin',
          errorCode: 'OCR_OR_PARSER_UNREADABLE',
        );
      }

      throw OrderApiException(
        message: e.message,
        errorCode: e.errorCode,
      );
    } on DioException catch (e) {
      throw OrderApiException(
        message: e.message ?? 'Fiş ayrıştırma sırasında bir hata oluştu',
      );
    }
  }

  /// POST /v1/orders/confirm - save user-confirmed order.
  Future<OrderConfirmResponse> confirmParsedOrder(
    OrderConfirmRequest request,
  ) async {
    try {
      final response = await _client.post(
        '/v1/orders/confirm',
        data: request.toJson(),
      );
      return OrderConfirmResponse.fromJson(
        response.data as Map<String, dynamic>,
      );
    } on ClientException catch (e) {
      throw OrderApiException(
        message: e.message,
        errorCode: e.errorCode,
      );
    } on DioException catch (e) {
      throw OrderApiException(
        message: e.message ?? 'Sipariş kaydedilirken bir hata oluştu',
      );
    }
  }
}
