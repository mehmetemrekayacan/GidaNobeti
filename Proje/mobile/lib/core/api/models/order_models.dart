/// Order history entry (single order in list)
class OrderHistoryEntry {
  final String id;
  final DateTime declaredAt;
  final DateTime? receiptDate;
  final double? totalAmount;
  final String method;
  final RestaurantSummary? restaurant;
  final List<OrderHistoryItem> items;

  OrderHistoryEntry({
    required this.id,
    required this.declaredAt,
    this.receiptDate,
    this.totalAmount,
    required this.method,
    this.restaurant,
    this.items = const [],
  });

  factory OrderHistoryEntry.fromJson(Map<String, dynamic> json) {
    final itemsList = json['items'] as List<dynamic>? ?? [];
    return OrderHistoryEntry(
      id: json['id'] as String,
      declaredAt: DateTime.parse(json['declared_at'] as String),
      receiptDate: json['receipt_date'] != null
          ? DateTime.tryParse(json['receipt_date'] as String)
          : null,
      totalAmount: (json['total_amount'] as num?)?.toDouble(),
      method: json['method'] as String,
      restaurant: json['restaurant'] != null
          ? RestaurantSummary.fromJson(
              json['restaurant'] as Map<String, dynamic>)
          : null,
      items: itemsList
          .map((e) => OrderHistoryItem.fromJson(e as Map<String, dynamic>))
          .toList(),
    );
  }
}

class RestaurantSummary {
  final int id;
  final String name;
  final String currentRiskStatus;

  RestaurantSummary({
    required this.id,
    required this.name,
    required this.currentRiskStatus,
  });

  factory RestaurantSummary.fromJson(Map<String, dynamic> json) {
    return RestaurantSummary(
      id: json['id'] as int,
      name: json['name'] as String,
      currentRiskStatus: json['current_risk_status'] as String,
    );
  }
}

class OrderHistoryItem {
  final String itemName;
  final int quantity;
  final double? unitPrice;

  OrderHistoryItem({
    required this.itemName,
    required this.quantity,
    this.unitPrice,
  });

  factory OrderHistoryItem.fromJson(Map<String, dynamic> json) {
    return OrderHistoryItem(
      itemName: json['item_name'] as String,
      quantity: json['quantity'] as int,
      unitPrice: (json['unit_price'] as num?)?.toDouble(),
    );
  }
}

/// Order history list response
class OrderHistoryListResponse {
  final int total;
  final int page;
  final int limit;
  final List<OrderHistoryEntry> items;

  OrderHistoryListResponse({
    required this.total,
    required this.page,
    required this.limit,
    required this.items,
  });

  factory OrderHistoryListResponse.fromJson(Map<String, dynamic> json) {
    final itemsList = json['items'] as List<dynamic>? ?? [];
    return OrderHistoryListResponse(
      total: json['total'] as int,
      page: json['page'] as int,
      limit: json['limit'] as int,
      items: itemsList
          .map((e) => OrderHistoryEntry.fromJson(e as Map<String, dynamic>))
          .toList(),
    );
  }
}

/// Order upload response
class OrderUploadResponse {
  final String orderId;
  final String? restaurantName;
  final int? restaurantId;
  final double? totalAmount;
  final String rawOcrText;
  final double ocrConfidence;
  final List<String> warnings;
  final DateTime? receiptDate;

  OrderUploadResponse({
    required this.orderId,
    this.restaurantName,
    this.restaurantId,
    this.totalAmount,
    required this.rawOcrText,
    required this.ocrConfidence,
    this.warnings = const [],
    this.receiptDate,
  });

  factory OrderUploadResponse.fromJson(Map<String, dynamic> json) {
    final warningsList = json['warnings'] as List<dynamic>? ?? [];
    return OrderUploadResponse(
      orderId: json['order_id'] as String,
      restaurantName: json['restaurant_name'] as String?,
      restaurantId: json['restaurant_id'] as int?,
      totalAmount: (json['total_amount'] as num?)?.toDouble(),
      rawOcrText: json['raw_ocr_text'] as String,
      ocrConfidence: (json['ocr_confidence'] as num).toDouble(),
      warnings: warningsList.map((e) => e as String).toList(),
      receiptDate: json['receipt_date'] != null
          ? DateTime.tryParse(json['receipt_date'] as String)
          : null,
    );
  }
}
