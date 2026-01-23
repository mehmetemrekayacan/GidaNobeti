import '../dio_client.dart';
import '../models/auth_models.dart';
import '../interceptors/auth_interceptor.dart';

/// Authentication API Service
class AuthApiService {
  final DioClient _client;

  AuthApiService(this._client);

  /// Register new user
  /// POST /v1/auth/register
  Future<TokenResponse> register(RegisterRequest request) async {
    try {
      final response = await _client.post(
        '/v1/auth/register',
        data: request.toJson(),
      );

      final tokenResponse = TokenResponse.fromJson(response.data);
      
      // Save token to storage
      await AuthInterceptor.saveToken(tokenResponse.accessToken);
      
      return tokenResponse;
    } catch (e) {
      rethrow;
    }
  }

  /// Login user
  /// POST /v1/auth/login
  Future<TokenResponse> login(LoginRequest request) async {
    try {
      final response = await _client.post(
        '/v1/auth/login',
        data: request.toJson(),
      );

      final tokenResponse = TokenResponse.fromJson(response.data);
      
      // Save token to storage
      await AuthInterceptor.saveToken(tokenResponse.accessToken);
      
      return tokenResponse;
    } catch (e) {
      rethrow;
    }
  }

  /// Logout user (clear local token)
  Future<void> logout() async {
    await AuthInterceptor.clearToken();
  }

  /// Check if user is authenticated
  Future<bool> isAuthenticated() async {
    final token = await AuthInterceptor.getToken();
    return token != null && token.isNotEmpty;
  }
}
