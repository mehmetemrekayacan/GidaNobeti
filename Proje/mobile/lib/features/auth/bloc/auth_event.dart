part of 'auth_bloc.dart';

/// Authentication events
abstract class AuthEvent extends Equatable {
  const AuthEvent();

  @override
  List<Object?> get props => [];
}

/// Check if user is already authenticated
class AuthCheckRequested extends AuthEvent {
  const AuthCheckRequested();
}

/// Login event
class AuthLoginRequested extends AuthEvent {
  final String tckn;
  final String password;

  const AuthLoginRequested({
    required this.tckn,
    required this.password,
  });

  @override
  List<Object?> get props => [tckn, password];
}

/// Register event
class AuthRegisterRequested extends AuthEvent {
  final String tckn;
  final String password;
  final String fullName;
  final String? email;
  final String? phone;
  final String? roomNumber;

  const AuthRegisterRequested({
    required this.tckn,
    required this.password,
    required this.fullName,
    this.email,
    this.phone,
    this.roomNumber,
  });

  @override
  List<Object?> get props => [tckn, password, fullName, email, phone, roomNumber];
}

/// Logout event
class AuthLogoutRequested extends AuthEvent {
  const AuthLogoutRequested();
}
