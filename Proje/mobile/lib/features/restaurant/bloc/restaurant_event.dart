part of 'restaurant_bloc.dart';

/// Restaurant Events
abstract class RestaurantEvent {
  const RestaurantEvent();
}

/// Load all restaurants
class RestaurantLoadRequested extends RestaurantEvent {
  const RestaurantLoadRequested();
}

/// Search restaurants by name
class RestaurantSearchRequested extends RestaurantEvent {
  final String query;

  const RestaurantSearchRequested(this.query);
}

/// Filter by district
class RestaurantFilterByDistrict extends RestaurantEvent {
  final String? district;

  const RestaurantFilterByDistrict(this.district);
}

/// Filter by platform
class RestaurantFilterByPlatform extends RestaurantEvent {
  final String? platform;

  const RestaurantFilterByPlatform(this.platform);
}

/// Filter by risk status
class RestaurantFilterByRiskStatus extends RestaurantEvent {
  final RiskStatus? riskStatus;

  const RestaurantFilterByRiskStatus(this.riskStatus);
}

/// Clear all filters
class RestaurantClearFilters extends RestaurantEvent {
  const RestaurantClearFilters();
}

/// Refresh restaurant list
class RestaurantRefreshRequested extends RestaurantEvent {
  const RestaurantRefreshRequested();
}
