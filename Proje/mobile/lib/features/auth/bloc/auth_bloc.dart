import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:equatable/equatable.dart';
import '../../../core/api/services/auth_api_service.dart';
import '../../../core/api/models/auth_models.dart';

part 'auth_event.dart';
part 'auth_state.dart';

/// Authentication BLoC - Handles login, register, logout logic
class AuthBloc extends Bloc<AuthEvent, AuthState> {
  final AuthApiService _authService;

  AuthBloc(this._authService) : super(const AuthInitial()) {
    on<AuthCheckRequested>(_onAuthCheckRequested);
    on<AuthLoginRequested>(_onAuthLoginRequested);
    on<AuthRegisterRequested>(_onAuthRegisterRequested);
    on<AuthLogoutRequested>(_onAuthLogoutRequested);
  }

  /// Check if user is already authenticated on app start
  Future<void> _onAuthCheckRequested(
    AuthCheckRequested event,
    Emitter<AuthState> emit,
  ) async {
    emit(const AuthLoading());

    try {
      final isAuth = await _authService.isAuthenticated();
      
      if (isAuth) {
        // Token exists - user is authenticated
        // Note: You may want to fetch user profile here
        emit(const AuthUnauthenticated()); // Temporary until we add profile API
      } else {
        emit(const AuthUnauthenticated());
      }
    } catch (e) {
      emit(const AuthUnauthenticated());
    }
  }

  /// Handle login request
  Future<void> _onAuthLoginRequested(
    AuthLoginRequested event,
    Emitter<AuthState> emit,
  ) async {
    emit(const AuthLoading());

    try {
      final request = LoginRequest(
        tckn: event.tckn,
        password: event.password,
      );

      final response = await _authService.login(request);

      emit(AuthAuthenticated(
        user: response.user,
        token: response.accessToken,
      ));
    } catch (e) {
      emit(AuthError(_getErrorMessage(e)));
    }
  }

  /// Handle register request
  Future<void> _onAuthRegisterRequested(
    AuthRegisterRequested event,
    Emitter<AuthState> emit,
  ) async {
    emit(const AuthLoading());

    try {
      final request = RegisterRequest(
        tckn: event.tckn,
        password: event.password,
        fullName: event.fullName,
        email: event.email,
        phone: event.phone,
        roomNumber: event.roomNumber,
      );

      final response = await _authService.register(request);

      emit(AuthAuthenticated(
        user: response.user,
        token: response.accessToken,
      ));
    } catch (e) {
      emit(AuthError(_getErrorMessage(e)));
    }
  }

  /// Handle logout request
  Future<void> _onAuthLogoutRequested(
    AuthLogoutRequested event,
    Emitter<AuthState> emit,
  ) async {
    emit(const AuthLoading());

    try {
      await _authService.logout();
      emit(const AuthUnauthenticated());
    } catch (e) {
      emit(AuthError(_getErrorMessage(e)));
    }
  }

  /// Extract user-friendly error message
  String _getErrorMessage(dynamic error) {
    final errorStr = error.toString().toLowerCase();
    
    if (errorStr.contains('invalid tckn or password') || 
        errorStr.contains('status: 401')) {
      return 'TC Kimlik No veya şifre hatalı';
    } else if (errorStr.contains('tckn already registered') || 
               errorStr.contains('status: 409')) {
      return 'Bu TC Kimlik No zaten kayıtlı';
    } else if (errorStr.contains('email already in use')) {
      return 'Bu e-posta adresi zaten kullanılıyor';
    } else if (errorStr.contains('connection timeout') || 
               errorStr.contains('timeoutexception')) {
      return 'Bağlantı zaman aşımına uğradı';
    } else if (errorStr.contains('network error') || 
               errorStr.contains('connectionerror')) {
      return 'Ağ bağlantısı hatası';
    } else {
      return 'Bir hata oluştu: ${error.toString()}';
    }
  }
}
