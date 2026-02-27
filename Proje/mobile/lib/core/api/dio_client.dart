import 'package:dio/dio.dart';
import '../config/app_config.dart';
import 'interceptors/auth_interceptor.dart';
import 'interceptors/logging_interceptor.dart';

/// Dio HTTP client configuration
class DioClient {
  /// Callback for 401 Unauthorized errors (token expired)
  static void Function()? onUnauthorized;

  static String get _baseUrl => AppConfig.apiBaseUrl;
  
  static const Duration _connectTimeout = Duration(seconds: 30);
  static const Duration _receiveTimeout = Duration(seconds: 30);

  late final Dio _dio;

  DioClient() {
    _dio = Dio(
      BaseOptions(
        baseUrl: _baseUrl,
        connectTimeout: _connectTimeout,
        receiveTimeout: _receiveTimeout,
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json',
        },
      ),
    );

    // Add interceptors
    _dio.interceptors.addAll([
      AuthInterceptor(),
      LoggingInterceptor(),
    ]);
  }

  /// GET request
  Future<Response> get(
    String path, {
    Map<String, dynamic>? queryParameters,
    Options? options,
  }) async {
    try {
      return await _dio.get(
        path,
        queryParameters: queryParameters,
        options: options,
      );
    } on DioException catch (e) {
      throw _handleError(e);
    }
  }

  /// POST request
  Future<Response> post(
    String path, {
    dynamic data,
    Map<String, dynamic>? queryParameters,
    Options? options,
  }) async {
    try {
      return await _dio.post(
        path,
        data: data,
        queryParameters: queryParameters,
        options: options,
      );
    } on DioException catch (e) {
      throw _handleError(e);
    }
  }

  /// POST multipart file (e.g. receipt image upload) - single file
  Future<Response> postMultipart(
    String path, {
    required String filePath,
    String fieldName = 'file',
  }) async {
    try {
      final formData = FormData.fromMap({
        fieldName: await MultipartFile.fromFile(filePath),
      });
      return await _dio.post(
        path,
        data: formData,
        options: Options(
          contentType: 'multipart/form-data',
          sendTimeout: const Duration(seconds: 60),
          receiveTimeout: const Duration(seconds: 60),
        ),
      );
    } on DioException catch (e) {
      throw _handleError(e);
    }
  }

  /// POST multipart files (multiple) - e.g. multi-page receipt upload
  Future<Response> postMultipartMultiple(
    String path, {
    required List<String> filePaths,
    String fieldName = 'files',
  }) async {
    try {
      final multipartFiles = <MultipartFile>[];
      for (final fp in filePaths) {
        multipartFiles.add(await MultipartFile.fromFile(fp));
      }
      final formData = FormData.fromMap({
        fieldName: multipartFiles,
      });
      return await _dio.post(
        path,
        data: formData,
        options: Options(
          contentType: 'multipart/form-data',
          sendTimeout: const Duration(seconds: 120),
          receiveTimeout: const Duration(seconds: 120),
        ),
      );
    } on DioException catch (e) {
      throw _handleError(e);
    }
  }

  /// PUT request
  Future<Response> put(
    String path, {
    dynamic data,
    Map<String, dynamic>? queryParameters,
    Options? options,
  }) async {
    try {
      return await _dio.put(
        path,
        data: data,
        queryParameters: queryParameters,
        options: options,
      );
    } on DioException catch (e) {
      throw _handleError(e);
    }
  }

  /// DELETE request
  Future<Response> delete(
    String path, {
    dynamic data,
    Map<String, dynamic>? queryParameters,
    Options? options,
  }) async {
    try {
      return await _dio.delete(
        path,
        data: data,
        queryParameters: queryParameters,
        options: options,
      );
    } on DioException catch (e) {
      throw _handleError(e);
    }
  }

  /// Handle Dio errors
  Exception _handleError(DioException error) {
    switch (error.type) {
      case DioExceptionType.connectionTimeout:
      case DioExceptionType.sendTimeout:
      case DioExceptionType.receiveTimeout:
        return TimeoutException('Connection timeout');
      case DioExceptionType.badResponse:
        return _handleResponseError(error.response!);
      case DioExceptionType.cancel:
        return RequestCancelledException('Request cancelled');
      default:
        return NetworkException('Network error: ${error.message}');
    }
  }

  /// Handle HTTP response errors
  Exception _handleResponseError(Response response) {
    final statusCode = response.statusCode ?? 0;
    final parsedError = _parseErrorPayload(response.data);
    final message = parsedError.message;
    final errorCode = parsedError.errorCode;

    // Handle 401 Unauthorized - trigger logout callback
    if (statusCode == 401) {
      onUnauthorized?.call();
      return ClientException(message, statusCode, errorCode: errorCode);
    }

    if (statusCode >= 400 && statusCode < 500) {
      return ClientException(message, statusCode, errorCode: errorCode);
    } else if (statusCode >= 500) {
      return ServerException(message, statusCode, errorCode: errorCode);
    }

    return UnknownException(message);
  }

  _ParsedApiError _parseErrorPayload(dynamic data) {
    if (data is Map<String, dynamic>) {
      final detail = data['detail'];
      if (detail is Map<String, dynamic>) {
        final nestedDetail = detail['detail'];
        final nestedCode = detail['error_code'];
        return _ParsedApiError(
          message: (nestedDetail is String && nestedDetail.isNotEmpty)
              ? nestedDetail
              : 'Unknown error',
          errorCode: nestedCode is String && nestedCode.isNotEmpty
              ? nestedCode
              : null,
        );
      }

      final directCode = data['error_code'];
      return _ParsedApiError(
        message: (detail is String && detail.isNotEmpty)
            ? detail
            : 'Unknown error',
        errorCode: directCode is String && directCode.isNotEmpty
            ? directCode
            : null,
      );
    }

    if (data is String && data.isNotEmpty) {
      return _ParsedApiError(message: data, errorCode: null);
    }

    return const _ParsedApiError(message: 'Unknown error', errorCode: null);
  }
}

class _ParsedApiError {
  final String message;
  final String? errorCode;

  const _ParsedApiError({required this.message, this.errorCode});
}

/// Custom exceptions
class TimeoutException implements Exception {
  final String message;
  TimeoutException(this.message);

  @override
  String toString() => message;
}

class RequestCancelledException implements Exception {
  final String message;
  RequestCancelledException(this.message);

  @override
  String toString() => message;
}

class NetworkException implements Exception {
  final String message;
  NetworkException(this.message);

  @override
  String toString() => message;
}

class ClientException implements Exception {
  final String message;
  final int statusCode;
  final String? errorCode;
  ClientException(this.message, this.statusCode, {this.errorCode});

  @override
  String toString() => errorCode == null
      ? '$message (Status: $statusCode)'
      : '$message (Code: $errorCode, Status: $statusCode)';
}

class ServerException implements Exception {
  final String message;
  final int statusCode;
  final String? errorCode;
  ServerException(this.message, this.statusCode, {this.errorCode});

  @override
  String toString() => errorCode == null
      ? '$message (Status: $statusCode)'
      : '$message (Code: $errorCode, Status: $statusCode)';
}

class UnknownException implements Exception {
  final String message;
  UnknownException(this.message);

  @override
  String toString() => message;
}
