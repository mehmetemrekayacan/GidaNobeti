/// App-wide constants
class AppConstants {
  // API Version
  static const String apiVersion = 'v1';
  
  // Storage Keys
  static const String keyAuthToken = 'auth_token';
  static const String keyUserId = 'user_id';
  static const String keyUserRole = 'user_role';
  
  // Validation
  static const int tcknLength = 11;
  static const int passwordMinLength = 8;
  static const int maxImageSizeMB = 5;
  
  // Timeouts
  static const Duration connectTimeout = Duration(seconds: 30);
  static const Duration receiveTimeout = Duration(seconds: 30);
}
