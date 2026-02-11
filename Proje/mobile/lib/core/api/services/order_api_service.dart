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
  }) async {
    final response = await _client.get(
      '/v1/orders/my-history',
      queryParameters: {'page': page, 'limit': limit},
    );
    return OrderHistoryListResponse.fromJson(
        response.data as Map<String, dynamic>);
  }

  /// POST /v1/orders/upload - upload receipt image
  Future<OrderUploadResponse> uploadReceipt(String filePath) async {
    final response = await _client.postMultipart(
      '/v1/orders/upload',
      filePath: filePath,
      fieldName: 'file',
    );
    return OrderUploadResponse.fromJson(
        response.data as Map<String, dynamic>);
  }
}
