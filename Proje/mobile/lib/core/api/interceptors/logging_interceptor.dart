import 'package:dio/dio.dart';
import 'package:flutter/foundation.dart';

/// HTTP Request/Response Logging Interceptor (Debug mode only)
class LoggingInterceptor extends Interceptor {
  @override
  void onRequest(RequestOptions options, RequestInterceptorHandler handler) {
    if (kDebugMode) {
      print('┌─────────────────────────────────────────────────');
      print('│ 🚀 REQUEST');
      print('│ ${options.method} ${options.uri}');
      print('│ Headers: ${options.headers}');
      if (options.data != null) {
        print('│ Body: ${options.data}');
      }
      if (options.queryParameters.isNotEmpty) {
        print('│ Query: ${options.queryParameters}');
      }
      print('└─────────────────────────────────────────────────');
    }
    handler.next(options);
  }

  @override
  void onResponse(Response response, ResponseInterceptorHandler handler) {
    if (kDebugMode) {
      print('┌─────────────────────────────────────────────────');
      print('│ ✅ RESPONSE');
      print('│ ${response.statusCode} ${response.requestOptions.method} ${response.requestOptions.uri}');
      print('│ Data: ${response.data}');
      print('└─────────────────────────────────────────────────');
    }
    handler.next(response);
  }

  @override
  void onError(DioException err, ErrorInterceptorHandler handler) {
    if (kDebugMode) {
      print('┌─────────────────────────────────────────────────');
      print('│ ❌ ERROR');
      print('│ ${err.requestOptions.method} ${err.requestOptions.uri}');
      print('│ Type: ${err.type}');
      print('│ Message: ${err.message}');
      if (err.response != null) {
        print('│ Status: ${err.response?.statusCode}');
        print('│ Data: ${err.response?.data}');
      }
      print('└─────────────────────────────────────────────────');
    }
    handler.next(err);
  }
}
