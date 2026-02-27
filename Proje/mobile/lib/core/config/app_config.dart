class AppConfig {
  AppConfig._();

  static const String _defaultApiBaseUrl = 'http://localhost:8000';

  static String get apiBaseUrl {
    const configured = String.fromEnvironment(
      'API_BASE_URL',
      defaultValue: _defaultApiBaseUrl,
    );
    if (configured.endsWith('/')) {
      return configured.substring(0, configured.length - 1);
    }
    return configured;
  }
}