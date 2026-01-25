/// Restaurant Risk Status Enum
enum RiskStatus {
  safe('SAFE'),
  watchlist('WATCHLIST'),
  redFlag('RED_FLAG'),
  blacklisted('BLACKLISTED');

  final String value;
  const RiskStatus(this.value);

  static RiskStatus fromString(String value) {
    return RiskStatus.values.firstWhere(
      (e) => e.value == value,
      orElse: () => RiskStatus.safe,
    );
  }
}

/// Restaurant Model
class Restaurant {
  final int id;
  final String name;
  final String? district;
  final String? platformOrigin;
  final RiskStatus riskStatus;
  final double? avgRating;
  final int totalOrders;
  final bool isActive;

  Restaurant({
    required this.id,
    required this.name,
    this.district,
    this.platformOrigin,
    required this.riskStatus,
    this.avgRating,
    required this.totalOrders,
    required this.isActive,
  });

  /// Create Restaurant from JSON
  factory Restaurant.fromJson(Map<String, dynamic> json) {
    return Restaurant(
      id: json['id'] as int,
      name: json['name'] as String,
      district: json['district'] as String?,
      platformOrigin: json['platform_origin'] as String?,
      riskStatus: RiskStatus.fromString(json['current_risk_status'] as String),
      avgRating: json['avg_rating'] != null 
          ? (json['avg_rating'] as num).toDouble() 
          : null,
      totalOrders: json['total_orders'] as int,
      isActive: json['is_active'] as bool,
    );
  }

  /// Convert Restaurant to JSON
  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'name': name,
      'district': district,
      'platform_origin': platformOrigin,
      'current_risk_status': riskStatus.value,
      'avg_rating': avgRating,
      'total_orders': totalOrders,
      'is_active': isActive,
    };
  }

  /// Create a copy with updated fields
  Restaurant copyWith({
    int? id,
    String? name,
    String? district,
    String? platformOrigin,
    RiskStatus? riskStatus,
    double? avgRating,
    int? totalOrders,
    bool? isActive,
  }) {
    return Restaurant(
      id: id ?? this.id,
      name: name ?? this.name,
      district: district ?? this.district,
      platformOrigin: platformOrigin ?? this.platformOrigin,
      riskStatus: riskStatus ?? this.riskStatus,
      avgRating: avgRating ?? this.avgRating,
      totalOrders: totalOrders ?? this.totalOrders,
      isActive: isActive ?? this.isActive,
    );
  }

  @override
  String toString() {
    return 'Restaurant(id: $id, name: $name, district: $district, rating: $avgRating)';
  }

  @override
  bool operator ==(Object other) {
    if (identical(this, other)) return true;
    return other is Restaurant && other.id == id;
  }

  @override
  int get hashCode => id.hashCode;
}
