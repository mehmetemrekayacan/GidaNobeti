import 'package:dio/dio.dart';
import '../dio_client.dart';
import '../models/order_models.dart';

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
    final response = await _client.postMultipartMultiple(
      '/v1/orders/upload',
      filePaths: filePaths,
      fieldName: 'files',
    );
    return OrderUploadResponse.fromJson(
        response.data as Map<String, dynamic>);
  }
}
