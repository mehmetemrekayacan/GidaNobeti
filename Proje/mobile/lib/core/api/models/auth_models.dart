/// User role enumeration
enum UserRole {
  student('STUDENT'),
  dormManager('DORM_MANAGER'),
  security('SECURITY'),
  sysAdmin('SYS_ADMIN');

  final String value;
  const UserRole(this.value);

  static UserRole fromString(String value) {
    return UserRole.values.firstWhere(
      (role) => role.value == value,
      orElse: () => UserRole.student,
    );
  }
}

/// User model
class User {
  final String id;
  final String tcknHash;
  final String fullName;
  final String? email;
  final String? phoneNumber;
  final String? roomNumber;
  final UserRole role;
  final bool isActive;
  final bool isVerified;
  final int? dormId;
  final DateTime createdAt;

  User({
    required this.id,
    required this.tcknHash,
    required this.fullName,
    this.email,
    this.phoneNumber,
    this.roomNumber,
    required this.role,
    required this.isActive,
    required this.isVerified,
    this.dormId,
    required this.createdAt,
  });

  factory User.fromJson(Map<String, dynamic> json) {
    return User(
      id: json['id'] as String,
      tcknHash: json['tckn_hash'] as String,
      fullName: json['full_name'] as String,
      email: json['email'] as String?,
      phoneNumber: json['phone_number'] as String?,
      roomNumber: json['room_number'] as String?,
      role: UserRole.fromString(json['role'] as String),
      isActive: json['is_active'] as bool,
      isVerified: json['is_verified'] as bool,
      dormId: json['dorm_id'] as int?,
      createdAt: DateTime.parse(json['created_at'] as String),
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'tckn_hash': tcknHash,
      'full_name': fullName,
      'email': email,
      'phone_number': phoneNumber,
      'room_number': roomNumber,
      'role': role.value,
      'is_active': isActive,
      'is_verified': isVerified,
      'dorm_id': dormId,
      'created_at': createdAt.toIso8601String(),
    };
  }
}

/// Token response from auth endpoints
class TokenResponse {
  final String accessToken;
  final String tokenType;
  final int expiresIn;
  final User user;

  TokenResponse({
    required this.accessToken,
    required this.tokenType,
    required this.expiresIn,
    required this.user,
  });

  factory TokenResponse.fromJson(Map<String, dynamic> json) {
    return TokenResponse(
      accessToken: json['access_token'] as String,
      tokenType: json['token_type'] as String,
      expiresIn: json['expires_in'] as int,
      user: User.fromJson(json['user'] as Map<String, dynamic>),
    );
  }
}

/// Register request model
class RegisterRequest {
  final String tckn;
  final String password;
  final String fullName;
  final String? email;
  final String? phone;
  final int? dormId;
  final String? roomNumber;

  RegisterRequest({
    required this.tckn,
    required this.password,
    required this.fullName,
    this.email,
    this.phone,
    this.dormId,
    this.roomNumber,
  });

  Map<String, dynamic> toJson() {
    return {
      'tckn': tckn,
      'password': password,
      'full_name': fullName,
      if (email != null) 'email': email,
      if (phone != null) 'phone': phone,
      if (dormId != null) 'dorm_id': dormId,
      if (roomNumber != null) 'room_number': roomNumber,
    };
  }
}

/// Login request model
class LoginRequest {
  final String tckn;
  final String password;

  LoginRequest({
    required this.tckn,
    required this.password,
  });

  Map<String, dynamic> toJson() {
    return {
      'tckn': tckn,
      'password': password,
    };
  }
}
