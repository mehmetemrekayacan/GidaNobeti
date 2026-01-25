part of 'restaurant_bloc.dart';

/// Restaurant States
abstract class RestaurantState extends Equatable {
  const RestaurantState();

  @override
  List<Object?> get props => [];
}

/// Initial state
class RestaurantInitial extends RestaurantState {
  const RestaurantInitial();
}

/// Loading state
class RestaurantLoading extends RestaurantState {
  const RestaurantLoading();
}

/// Success state with restaurant list
class RestaurantLoaded extends RestaurantState {
  final List<Restaurant> restaurants;
  final String? activeDistrict;
  final String? activePlatform;
  final RiskStatus? activeRiskStatus;
  final String? searchQuery;

  const RestaurantLoaded({
    required this.restaurants,
    this.activeDistrict,
    this.activePlatform,
    this.activeRiskStatus,
    this.searchQuery,
  });

  @override
  List<Object?> get props => [
        restaurants,
        activeDistrict,
        activePlatform,
        activeRiskStatus,
        searchQuery,
      ];

  /// Check if any filters are active
  bool get hasActiveFilters =>
      activeDistrict != null ||
      activePlatform != null ||
      activeRiskStatus != null ||
      (searchQuery != null && searchQuery!.isNotEmpty);

  /// Copy with new values
  RestaurantLoaded copyWith({
    List<Restaurant>? restaurants,
    String? activeDistrict,
    String? activePlatform,
    RiskStatus? activeRiskStatus,
    String? searchQuery,
    bool clearDistrict = false,
    bool clearPlatform = false,
    bool clearRiskStatus = false,
    bool clearSearchQuery = false,
  }) {
    return RestaurantLoaded(
      restaurants: restaurants ?? this.restaurants,
      activeDistrict: clearDistrict ? null : (activeDistrict ?? this.activeDistrict),
      activePlatform: clearPlatform ? null : (activePlatform ?? this.activePlatform),
      activeRiskStatus: clearRiskStatus ? null : (activeRiskStatus ?? this.activeRiskStatus),
      searchQuery: clearSearchQuery ? null : (searchQuery ?? this.searchQuery),
    );
  }
}

/// Error state
class RestaurantError extends RestaurantState {
  final String message;

  const RestaurantError(this.message);

  @override
  List<Object?> get props => [message];
}
