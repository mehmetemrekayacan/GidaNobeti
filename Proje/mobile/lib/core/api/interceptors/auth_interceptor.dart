import 'package:dio/dio.dart';
import 'package:flutter/foundation.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';

import 'dart:convert';

/// JWT Token Interceptor - Automatically inject token into requests
class AuthInterceptor extends Interceptor {
  static const String _tokenKey = 'auth_token';
  static const String _userKey = 'auth_user';
  static const FlutterSecureStorage _secureStorage = FlutterSecureStorage();

  @override
  void onRequest(
    RequestOptions options,
    RequestInterceptorHandler handler,
  ) async {
    try {
      final token = await _secureStorage.read(key: _tokenKey);

      if (token != null && token.isNotEmpty) {
        options.headers['Authorization'] = 'Bearer $token';
      }
    } catch (e) {
      if (kDebugMode) {
        debugPrint('AuthInterceptor.onRequest token read error: $e');
      }
    }

    handler.next(options);
  }

  @override
  void onError(DioException err, ErrorInterceptorHandler handler) async {
    // Handle 401 Unauthorized - token expired or invalid
    if (err.response?.statusCode == 401) {
      try {
        await _secureStorage.delete(key: _tokenKey);
        await _secureStorage.delete(key: _userKey);
      } catch (e) {
        if (kDebugMode) {
          debugPrint('AuthInterceptor.onError secure clear error: $e');
        }
      }
    }

    handler.next(err);
  }

  /// Save token to storage
  static Future<void> saveToken(String token) async {
    try {
      await _secureStorage.write(key: _tokenKey, value: token);
    } catch (e) {
      if (kDebugMode) {
        debugPrint('AuthInterceptor.saveToken error: $e');
      }
      rethrow;
    }
  }

  /// Save user JSON (for session restore)
  static Future<void> saveUser(Map<String, dynamic> userJson) async {
    try {
      await _secureStorage.write(key: _userKey, value: jsonEncode(userJson));
    } catch (e) {
      if (kDebugMode) {
        debugPrint('AuthInterceptor.saveUser error: $e');
      }
      rethrow;
    }
  }

  /// Get token from storage
  static Future<String?> getToken() async {
    try {
      return await _secureStorage.read(key: _tokenKey);
    } catch (e) {
      if (kDebugMode) {
        debugPrint('AuthInterceptor.getToken error: $e');
      }
      return null;
    }
  }

  /// Get saved user JSON (for session restore)
  static Future<Map<String, dynamic>?> getUserJson() async {
    try {
      final raw = await _secureStorage.read(key: _userKey);
      if (raw == null || raw.isEmpty) return null;
      return jsonDecode(raw) as Map<String, dynamic>;
    } catch (e) {
      if (kDebugMode) {
        debugPrint('AuthInterceptor.getUserJson error: $e');
      }
      return null;
    }
  }

  /// Clear token and user from storage
  static Future<void> clearToken() async {
    try {
      await _secureStorage.delete(key: _tokenKey);
      await _secureStorage.delete(key: _userKey);
    } catch (e) {
      if (kDebugMode) {
        debugPrint('AuthInterceptor.clearToken error: $e');
      }
      rethrow;
    }
  }
}
