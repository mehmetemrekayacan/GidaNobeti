import 'package:dio/dio.dart';
import '../dio_client.dart';
import '../models/order_models.dart';

class OrderUploadException implements Exception {
  final String message;
  final String? errorCode;

  const OrderUploadException({required this.message, this.errorCode});

  @override
  String toString() => message;
}

/// Order API Service - upload receipt & order history
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

  /// POST /v1/orders/upload - upload single receipt image (backward compat)
  Future<OrderUploadResponse> uploadReceipt(String filePath) async {
    return uploadReceipts([filePath]);
  }

  /// POST /v1/orders/upload - upload one or more receipt images
  /// Trendyol gibi uzun fişler için max 2 görsel destekler.
  Future<OrderUploadResponse> uploadReceipts(List<String> filePaths) async {
    try {
      final response = await _client.postMultipartMultiple(
        '/v1/orders/upload',
        filePaths: filePaths,
        fieldName: 'files',
      );
      return OrderUploadResponse.fromJson(
          response.data as Map<String, dynamic>);
    } on ClientException catch (e) {
      const readableCodes = {
        'OCR_UNREADABLE',
        'PARSER_RESTAURANT_NOT_FOUND',
      };

      if (e.statusCode == 400 && readableCodes.contains(e.errorCode)) {
        throw const OrderUploadException(
          message:
              'Fiş okunamadı veya restoran tespit edilemedi, lütfen daha net bir fotoğraf çekin',
          errorCode: 'OCR_OR_PARSER_UNREADABLE',
        );
      }

      throw OrderUploadException(
        message: e.message,
        errorCode: e.errorCode,
      );
    } on DioException catch (e) {
      throw OrderUploadException(
        message: e.message ?? 'Sipariş yükleme sırasında bir hata oluştu',
      );
    }
  }
}
