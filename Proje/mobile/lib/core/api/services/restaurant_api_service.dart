import 'package:dio/dio.dart';
import '../dio_client.dart';
import '../models/restaurant_models.dart';

/// Restaurant API Service
class RestaurantApiService {
  final DioClient _dioClient;

  RestaurantApiService({DioClient? dioClient})
      : _dioClient = dioClient ?? DioClient();

  /// Get list of restaurants with optional filters
  Future<List<Restaurant>> getRestaurants({
    String? name,
    String? district,
    String? platform,
    String? riskStatus,
    bool? isActive,
    int skip = 0,
    int limit = 100,
  }) async {
    try {
      final queryParams = <String, dynamic>{};
      
      if (name != null) queryParams['name'] = name;
      if (district != null) queryParams['district'] = district;
      if (platform != null) queryParams['platform'] = platform;
      if (riskStatus != null) queryParams['risk_status'] = riskStatus;
      if (isActive != null) queryParams['is_active'] = isActive;
      queryParams['skip'] = skip;
      queryParams['limit'] = limit;

      final response = await _dioClient.get(
        '/v1/restaurants',
        queryParameters: queryParams,
      );

      if (response.data is List) {
        return (response.data as List)
            .map((json) => Restaurant.fromJson(json as Map<String, dynamic>))
            .toList();
      }

      return [];
    } on DioException catch (e) {
      throw _handleError(e);
    }
  }

  /// Get single restaurant by ID
  Future<Restaurant> getRestaurant(int restaurantId) async {
    try {
      final response = await _dioClient.get('/v1/restaurants/$restaurantId');
      return Restaurant.fromJson(response.data as Map<String, dynamic>);
    } on DioException catch (e) {
      throw _handleError(e);
    }
  }

  /// Get restaurant statistics
  Future<Map<String, dynamic>> getRestaurantStats() async {
    try {
      final response = await _dioClient.get('/v1/restaurants/stats/summary');
      return response.data as Map<String, dynamic>;
    } on DioException catch (e) {
      throw _handleError(e);
    }
  }

  /// Search restaurants by name
  Future<List<Restaurant>> searchRestaurants(String query) async {
    return getRestaurants(name: query);
  }

  /// Filter restaurants by district
  Future<List<Restaurant>> getRestaurantsByDistrict(String district) async {
    return getRestaurants(district: district);
  }

  /// Filter restaurants by platform
  Future<List<Restaurant>> getRestaurantsByPlatform(String platform) async {
    return getRestaurants(platform: platform);
  }

  /// Filter restaurants by risk status
  Future<List<Restaurant>> getRestaurantsByRiskStatus(
      RiskStatus riskStatus) async {
    return getRestaurants(riskStatus: riskStatus.value);
  }

  /// Handle Dio errors
  Exception _handleError(DioException e) {
    if (e.response != null) {
      final statusCode = e.response?.statusCode;
      final message = e.response?.data['detail'] ?? 'An error occurred';
      
      switch (statusCode) {
        case 404:
          return Exception('Restaurant not found');
        case 500:
          return Exception('Server error: $message');
        default:
          return Exception(message);
      }
    } else if (e.type == DioExceptionType.connectionTimeout ||
        e.type == DioExceptionType.receiveTimeout) {
      return Exception('Connection timeout. Please check your internet.');
    } else if (e.type == DioExceptionType.connectionError) {
      return Exception('No internet connection');
    } else {
      return Exception('Unexpected error: ${e.message}');
    }
  }
}
