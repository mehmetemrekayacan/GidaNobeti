import 'package:flutter/foundation.dart';

class AppConfig {
  AppConfig._();

  // USB tüneli (adb reverse) kullandığımız için artık localhost diyoruz
  static const String _apiBaseUrl = 'http://127.0.0.1:8000';

  static String get apiBaseUrl {
    return _apiBaseUrl;
  }
}