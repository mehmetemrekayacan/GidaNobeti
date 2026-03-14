/// Order history entry (single order in list)
class OrderHistoryEntry {
  final String id;
  final DateTime declaredAt;
  final DateTime? receiptDate;
  final double? totalAmount;
  final String? foodContent;
  final String method;
  final RestaurantSummary? restaurant;
  final List<OrderHistoryItem> items;

  OrderHistoryEntry({
    required this.id,
    required this.declaredAt,
    this.receiptDate,
    this.totalAmount,
    this.foodContent,
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
      foodContent: json['food_content'] as String?,
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
class OrderDraftItem {
  final String itemName;
  final int quantity;
  final double? unitPrice;

  OrderDraftItem({
    required this.itemName,
    required this.quantity,
    this.unitPrice,
  });

  factory OrderDraftItem.fromJson(Map<String, dynamic> json) {
    return OrderDraftItem(
      itemName: json['item_name'] as String,
      quantity: json['quantity'] as int,
      unitPrice: (json['unit_price'] as num?)?.toDouble(),
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'item_name': itemName,
      'quantity': quantity,
      'unit_price': unitPrice,
    };
  }
}

class OrderParseResponse {
  final String? restaurantName;
  final int? restaurantId;
  final double? totalAmount;
  final String? foodContent;
  final String rawOcrText;
  final double ocrConfidence;
  final List<String> warnings;
  final DateTime? receiptDate;
  final List<OrderDraftItem> items;

  OrderParseResponse({
    this.restaurantName,
    this.restaurantId,
    this.totalAmount,
    this.foodContent,
    required this.rawOcrText,
    required this.ocrConfidence,
    this.warnings = const [],
    this.receiptDate,
    this.items = const [],
  });

  factory OrderParseResponse.fromJson(Map<String, dynamic> json) {
    final warningsList = json['warnings'] as List<dynamic>? ?? [];
    final itemsList = json['items'] as List<dynamic>? ?? [];
    return OrderParseResponse(
      restaurantName: json['restaurant_name'] as String?,
      restaurantId: json['restaurant_id'] as int?,
      totalAmount: (json['total_amount'] as num?)?.toDouble(),
      foodContent: json['food_content'] as String?,
      rawOcrText: json['raw_ocr_text'] as String,
      ocrConfidence: (json['ocr_confidence'] as num).toDouble(),
      warnings: warningsList.map((e) => e as String).toList(),
      receiptDate: json['receipt_date'] != null
          ? DateTime.tryParse(json['receipt_date'] as String)
          : null,
      items: itemsList
          .map((e) => OrderDraftItem.fromJson(e as Map<String, dynamic>))
          .toList(),
    );
  }
}

class OrderConfirmRequest {
  final String restaurantName;
  final double? totalAmount;
  final String? foodContent;
  final String rawOcrText;
  final double ocrConfidence;
  final List<String> warnings;
  final DateTime? receiptDate;
  final List<OrderDraftItem> items;

  OrderConfirmRequest({
    required this.restaurantName,
    this.totalAmount,
    this.foodContent,
    required this.rawOcrText,
    required this.ocrConfidence,
    this.warnings = const [],
    this.receiptDate,
    this.items = const [],
  });

  Map<String, dynamic> toJson() {
    return {
      'restaurant_name': restaurantName,
      'total_amount': totalAmount,
      'food_content': foodContent,
      'raw_ocr_text': rawOcrText,
      'ocr_confidence': ocrConfidence,
      'warnings': warnings,
      'receipt_date': receiptDate?.toIso8601String(),
      'items': items.map((item) => item.toJson()).toList(),
    };
  }
}

class OrderConfirmResponse {
  final String orderId;
  final String? restaurantName;
  final int? restaurantId;
  final double? totalAmount;
  final String? foodContent;
  final String rawOcrText;
  final double ocrConfidence;
  final List<String> warnings;
  final DateTime? receiptDate;
  final List<OrderDraftItem> items;

  OrderConfirmResponse({
    required this.orderId,
    this.restaurantName,
    this.restaurantId,
    this.totalAmount,
    this.foodContent,
    required this.rawOcrText,
    required this.ocrConfidence,
    this.warnings = const [],
    this.receiptDate,
    this.items = const [],
  });

  factory OrderConfirmResponse.fromJson(Map<String, dynamic> json) {
    final warningsList = json['warnings'] as List<dynamic>? ?? [];
    final itemsList = json['items'] as List<dynamic>? ?? [];
    return OrderConfirmResponse(
      orderId: json['order_id'] as String,
      restaurantName: json['restaurant_name'] as String?,
      restaurantId: json['restaurant_id'] as int?,
      totalAmount: (json['total_amount'] as num?)?.toDouble(),
      foodContent: json['food_content'] as String?,
      rawOcrText: json['raw_ocr_text'] as String,
      ocrConfidence: (json['ocr_confidence'] as num).toDouble(),
      warnings: warningsList.map((e) => e as String).toList(),
      receiptDate: json['receipt_date'] != null
          ? DateTime.tryParse(json['receipt_date'] as String)
          : null,
      items: itemsList
          .map((e) => OrderDraftItem.fromJson(e as Map<String, dynamic>))
          .toList(),
    );
  }
}
