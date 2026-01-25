import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:equatable/equatable.dart';
import '../../../core/api/models/restaurant_models.dart';
import '../../../core/api/services/restaurant_api_service.dart';

part 'restaurant_event.dart';
part 'restaurant_state.dart';

/// Restaurant BLoC - Manages restaurant list and filters
class RestaurantBloc extends Bloc<RestaurantEvent, RestaurantState> {
  final RestaurantApiService _restaurantService;

  RestaurantBloc({RestaurantApiService? restaurantService})
      : _restaurantService = restaurantService ?? RestaurantApiService(),
        super(const RestaurantInitial()) {
    on<RestaurantLoadRequested>(_onLoadRequested);
    on<RestaurantSearchRequested>(_onSearchRequested);
    on<RestaurantFilterByDistrict>(_onFilterByDistrict);
    on<RestaurantFilterByPlatform>(_onFilterByPlatform);
    on<RestaurantFilterByRiskStatus>(_onFilterByRiskStatus);
    on<RestaurantClearFilters>(_onClearFilters);
    on<RestaurantRefreshRequested>(_onRefreshRequested);
  }

  /// Load all restaurants
  Future<void> _onLoadRequested(
    RestaurantLoadRequested event,
    Emitter<RestaurantState> emit,
  ) async {
    emit(const RestaurantLoading());

    try {
      final restaurants = await _restaurantService.getRestaurants();
      emit(RestaurantLoaded(restaurants: restaurants));
    } catch (e) {
      emit(RestaurantError(e.toString()));
    }
  }

  /// Search restaurants by name
  Future<void> _onSearchRequested(
    RestaurantSearchRequested event,
    Emitter<RestaurantState> emit,
  ) async {
    final currentState = state;
    
    emit(const RestaurantLoading());

    try {
      final restaurants = event.query.isEmpty
          ? await _restaurantService.getRestaurants()
          : await _restaurantService.searchRestaurants(event.query);

      if (currentState is RestaurantLoaded) {
        emit(currentState.copyWith(
          restaurants: restaurants,
          searchQuery: event.query.isEmpty ? null : event.query,
          clearSearchQuery: event.query.isEmpty,
        ));
      } else {
        emit(RestaurantLoaded(
          restaurants: restaurants,
          searchQuery: event.query.isEmpty ? null : event.query,
        ));
      }
    } catch (e) {
      emit(RestaurantError(e.toString()));
    }
  }

  /// Filter by district
  Future<void> _onFilterByDistrict(
    RestaurantFilterByDistrict event,
    Emitter<RestaurantState> emit,
  ) async {
    final currentState = state;
    
    emit(const RestaurantLoading());

    try {
      final restaurants = event.district == null
          ? await _restaurantService.getRestaurants()
          : await _restaurantService.getRestaurantsByDistrict(event.district!);

      if (currentState is RestaurantLoaded) {
        emit(currentState.copyWith(
          restaurants: restaurants,
          activeDistrict: event.district,
          clearDistrict: event.district == null,
        ));
      } else {
        emit(RestaurantLoaded(
          restaurants: restaurants,
          activeDistrict: event.district,
        ));
      }
    } catch (e) {
      emit(RestaurantError(e.toString()));
    }
  }

  /// Filter by platform
  Future<void> _onFilterByPlatform(
    RestaurantFilterByPlatform event,
    Emitter<RestaurantState> emit,
  ) async {
    final currentState = state;
    
    emit(const RestaurantLoading());

    try {
      final restaurants = event.platform == null
          ? await _restaurantService.getRestaurants()
          : await _restaurantService.getRestaurantsByPlatform(event.platform!);

      if (currentState is RestaurantLoaded) {
        emit(currentState.copyWith(
          restaurants: restaurants,
          activePlatform: event.platform,
          clearPlatform: event.platform == null,
        ));
      } else {
        emit(RestaurantLoaded(
          restaurants: restaurants,
          activePlatform: event.platform,
        ));
      }
    } catch (e) {
      emit(RestaurantError(e.toString()));
    }
  }

  /// Filter by risk status
  Future<void> _onFilterByRiskStatus(
    RestaurantFilterByRiskStatus event,
    Emitter<RestaurantState> emit,
  ) async {
    final currentState = state;
    
    emit(const RestaurantLoading());

    try {
      final restaurants = event.riskStatus == null
          ? await _restaurantService.getRestaurants()
          : await _restaurantService.getRestaurantsByRiskStatus(
              event.riskStatus!);

      if (currentState is RestaurantLoaded) {
        emit(currentState.copyWith(
          restaurants: restaurants,
          activeRiskStatus: event.riskStatus,
          clearRiskStatus: event.riskStatus == null,
        ));
      } else {
        emit(RestaurantLoaded(
          restaurants: restaurants,
          activeRiskStatus: event.riskStatus,
        ));
      }
    } catch (e) {
      emit(RestaurantError(e.toString()));
    }
  }

  /// Clear all filters
  Future<void> _onClearFilters(
    RestaurantClearFilters event,
    Emitter<RestaurantState> emit,
  ) async {
    emit(const RestaurantLoading());

    try {
      final restaurants = await _restaurantService.getRestaurants();
      emit(RestaurantLoaded(restaurants: restaurants));
    } catch (e) {
      emit(RestaurantError(e.toString()));
    }
  }

  /// Refresh restaurant list
  Future<void> _onRefreshRequested(
    RestaurantRefreshRequested event,
    Emitter<RestaurantState> emit,
  ) async {
    try {
      final restaurants = await _restaurantService.getRestaurants();
      
      if (state is RestaurantLoaded) {
        final currentState = state as RestaurantLoaded;
        emit(currentState.copyWith(restaurants: restaurants));
      } else {
        emit(RestaurantLoaded(restaurants: restaurants));
      }
    } catch (e) {
      // Keep current state on refresh error
      if (state is! RestaurantLoaded) {
        emit(RestaurantError(e.toString()));
      }
    }
  }
}
