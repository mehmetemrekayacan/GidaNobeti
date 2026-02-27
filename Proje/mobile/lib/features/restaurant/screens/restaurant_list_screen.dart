import 'dart:async';
import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:go_router/go_router.dart';
import '../bloc/restaurant_bloc.dart';
import '../../../core/api/models/restaurant_models.dart';
import '../../../core/router/app_routes.dart';

class RestaurantListScreen extends StatelessWidget {
  const RestaurantListScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return BlocProvider(
      create: (context) => RestaurantBloc()..add(const RestaurantLoadRequested()),
      child: const _RestaurantListView(),
    );
  }
}

class _RestaurantListView extends StatefulWidget {
  const _RestaurantListView();

  @override
  State<_RestaurantListView> createState() => _RestaurantListViewState();
}

class _RestaurantListViewState extends State<_RestaurantListView> {
  final _searchController = TextEditingController();
  Timer? _debounce;

  @override
  void dispose() {
    _searchController.dispose();
    _debounce?.cancel();
    super.dispose();
  }

  void _onSearchChanged(String query) {
    _debounce?.cancel();
    _debounce = Timer(const Duration(milliseconds: 500), () {
      if (query.isEmpty) {
        context.read<RestaurantBloc>().add(const RestaurantLoadRequested());
      } else {
        context.read<RestaurantBloc>().add(RestaurantSearchRequested(query));
      }
    });
  }

  void _showFilterSheet() {
    showModalBottomSheet(
      context: context,
      builder: (context) => _FilterBottomSheet(
        bloc: context.read<RestaurantBloc>(),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Restoranlar'),
        actions: [
          IconButton(
            icon: const Icon(Icons.filter_list),
            onPressed: _showFilterSheet,
          ),
        ],
      ),
      body: Column(
        children: [
          // Search Bar
          Padding(
            padding: const EdgeInsets.all(16.0),
            child: TextField(
              controller: _searchController,
              decoration: InputDecoration(
                hintText: 'Restoran ara...',
                prefixIcon: const Icon(Icons.search),
                suffixIcon: _searchController.text.isNotEmpty
                    ? IconButton(
                        icon: const Icon(Icons.clear),
                        onPressed: () {
                          _searchController.clear();
                          _onSearchChanged('');
                        },
                      )
                    : null,
                border: OutlineInputBorder(
                  borderRadius: BorderRadius.circular(12),
                ),
                filled: true,
                fillColor: Colors.grey[100],
              ),
              onChanged: _onSearchChanged,
            ),
          ),
          // Active Filters
          BlocBuilder<RestaurantBloc, RestaurantState>(
            builder: (context, state) {
              if (state is RestaurantLoaded && state.hasActiveFilters) {
                return Container(
                  padding: const EdgeInsets.symmetric(horizontal: 16),
                  height: 50,
                  child: ListView(
                    scrollDirection: Axis.horizontal,
                    children: [
                      if (state.activeDistrict != null)
                        Chip(
                          label: Text('Bölge: ${state.activeDistrict}'),
                          onDeleted: () => context
                              .read<RestaurantBloc>()
                              .add(const RestaurantClearFilters()),
                          deleteIcon: const Icon(Icons.close, size: 18),
                        ),
                      if (state.activePlatform != null) ...[
                        const SizedBox(width: 8),
                        Chip(
                          label: Text('Platform: ${state.activePlatform}'),
                          onDeleted: () => context
                              .read<RestaurantBloc>()
                              .add(const RestaurantClearFilters()),
                          deleteIcon: const Icon(Icons.close, size: 18),
                        ),
                      ],
                      if (state.activeRiskStatus != null) ...[
                        const SizedBox(width: 8),
                        Chip(
                          label: Text(_getRiskLabel(state.activeRiskStatus!)),
                          onDeleted: () => context
                              .read<RestaurantBloc>()
                              .add(const RestaurantClearFilters()),
                          deleteIcon: const Icon(Icons.close, size: 18),
                        ),
                      ],
                      const SizedBox(width: 8),
                      TextButton.icon(
                        onPressed: () => context
                            .read<RestaurantBloc>()
                            .add(const RestaurantClearFilters()),
                        icon: const Icon(Icons.clear_all, size: 18),
                        label: const Text('Tümünü Temizle'),
                      ),
                    ],
                  ),
                );
              }
              return const SizedBox.shrink();
            },
          ),
          // Restaurant List
          Expanded(
            child: BlocBuilder<RestaurantBloc, RestaurantState>(
        builder: (context, state) {
          if (state is RestaurantLoading) {
            return const Center(child: CircularProgressIndicator());
          }

          if (state is RestaurantError) {
            return Center(
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  const Icon(Icons.error_outline, size: 64, color: Colors.red),
                  const SizedBox(height: 16),
                  Text(
                    state.message,
                    textAlign: TextAlign.center,
                    style: const TextStyle(fontSize: 16),
                  ),
                  const SizedBox(height: 24),
                  ElevatedButton.icon(
                    onPressed: () {
                      context
                          .read<RestaurantBloc>()
                          .add(const RestaurantLoadRequested());
                    },
                    icon: const Icon(Icons.refresh),
                    label: const Text('Tekrar Dene'),
                  ),
                ],
              ),
            );
          }

          if (state is RestaurantLoaded) {
            if (state.restaurants.isEmpty) {
              return Center(
                child: Column(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    const Icon(Icons.restaurant, size: 64, color: Colors.grey),
                    const SizedBox(height: 16),
                    Text(
                      state.hasActiveFilters
                          ? 'Filtre kriterlerine uygun restoran bulunamadı'
                          : 'Henüz restoran eklenmemiş',
                      style: const TextStyle(fontSize: 16, color: Colors.grey),
                    ),
                    if (state.hasActiveFilters) ...[
                      const SizedBox(height: 24),
                      TextButton.icon(
                        onPressed: () {
                          context
                              .read<RestaurantBloc>()
                              .add(const RestaurantClearFilters());
                        },
                        icon: const Icon(Icons.clear),
                        label: const Text('Filtreleri Temizle'),
                      ),
                    ],
                  ],
                ),
              );
            }

            return RefreshIndicator(
              onRefresh: () async {
                context
                    .read<RestaurantBloc>()
                    .add(const RestaurantRefreshRequested());
              },
              child: ListView.builder(
                padding: const EdgeInsets.all(16),
                itemCount: state.restaurants.length,
                itemBuilder: (context, index) {
                  final restaurant = state.restaurants[index];
                  return RestaurantCard(restaurant: restaurant);
                },
              ),
            );
          }

          return const SizedBox();
        },
      ),
          ),
        ],
      ),
    );
  }

  String _getRiskLabel(RiskStatus status) {
    switch (status) {
      case RiskStatus.safe:
        return 'Güvenli';
      case RiskStatus.watchlist:
        return 'Takipte';
      case RiskStatus.redFlag:
        return 'Riskli';
      case RiskStatus.blacklisted:
        return 'Kara Liste';
    }
  }
}

class _FilterBottomSheet extends StatelessWidget {
  final RestaurantBloc bloc;

  const _FilterBottomSheet({required this.bloc});

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(24),
      child: Column(
        mainAxisSize: MainAxisSize.min,
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              const Text(
                'Filtrele',
                style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold),
              ),
              TextButton(
                onPressed: () {
                  bloc.add(const RestaurantClearFilters());
                  Navigator.pop(context);
                },
                child: const Text('Temizle'),
              ),
            ],
          ),
          const SizedBox(height: 24),
          const Text('Risk Durumu', style: TextStyle(fontWeight: FontWeight.w600)),
          const SizedBox(height: 8),
          Wrap(
            spacing: 8,
            children: [
              FilterChip(
                label: const Text('Güvenli'),
                avatar: const Icon(Icons.check_circle, size: 18, color: Colors.green),
                onSelected: (selected) {
                  bloc.add(const RestaurantFilterByRiskStatus(RiskStatus.safe));
                  Navigator.pop(context);
                },
              ),
              FilterChip(
                label: const Text('Takipte'),
                avatar: const Icon(Icons.warning, size: 18, color: Colors.orange),
                onSelected: (selected) {
                  bloc.add(const RestaurantFilterByRiskStatus(RiskStatus.watchlist));
                  Navigator.pop(context);
                },
              ),
              FilterChip(
                label: const Text('Riskli'),
                avatar: const Icon(Icons.flag, size: 18, color: Colors.red),
                onSelected: (selected) {
                  bloc.add(const RestaurantFilterByRiskStatus(RiskStatus.redFlag));
                  Navigator.pop(context);
                },
              ),
              FilterChip(
                label: const Text('Kara Liste'),
                avatar: const Icon(Icons.block, size: 18),
                onSelected: (selected) {
                  bloc.add(const RestaurantFilterByRiskStatus(RiskStatus.blacklisted));
                  Navigator.pop(context);
                },
              ),
            ],
          ),
          const SizedBox(height: 16),
          const Text('Platform', style: TextStyle(fontWeight: FontWeight.w600)),
          const SizedBox(height: 8),
          Wrap(
            spacing: 8,
            children: [
              FilterChip(
                label: const Text('Trendyol'),
                onSelected: (selected) {
                  bloc.add(const RestaurantFilterByPlatform('Trendyol'));
                  Navigator.pop(context);
                },
              ),
              FilterChip(
                label: const Text('Getir'),
                onSelected: (selected) {
                  bloc.add(const RestaurantFilterByPlatform('Getir'));
                  Navigator.pop(context);
                },
              ),
              FilterChip(
                label: const Text('Yemeksepeti'),
                onSelected: (selected) {
                  bloc.add(const RestaurantFilterByPlatform('Yemeksepeti'));
                  Navigator.pop(context);
                },
              ),
            ],
          ),
        ],
      ),
    );
  }
}

/// Restaurant Card Widget
class RestaurantCard extends StatelessWidget {
  final Restaurant restaurant;

  const RestaurantCard({super.key, required this.restaurant});

  @override
  Widget build(BuildContext context) {
    return Card(
      margin: const EdgeInsets.only(bottom: 12),
      child: InkWell(
        onTap: () {
          context.pushNamed(
            AppRoutes.restaurantDetailName,
            pathParameters: AppRoutes.restaurantDetailParameters(restaurant.id),
          );
        },
        borderRadius: BorderRadius.circular(12),
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // Restaurant name and risk badge
              Row(
                children: [
                  Expanded(
                    child: Text(
                      restaurant.name,
                      style: const TextStyle(
                        fontSize: 18,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                  ),
                  _buildRiskBadge(restaurant.riskStatus),
                ],
              ),

              const SizedBox(height: 8),

              // District and platform
              Row(
                children: [
                  if (restaurant.district != null) ...[
                    const Icon(Icons.location_on, size: 16, color: Colors.grey),
                    const SizedBox(width: 4),
                    Text(
                      restaurant.district!,
                      style: const TextStyle(color: Colors.grey),
                    ),
                  ],
                  if (restaurant.district != null &&
                      restaurant.platformOrigin != null)
                    const SizedBox(width: 16),
                  if (restaurant.platformOrigin != null) ...[
                    const Icon(Icons.delivery_dining,
                        size: 16, color: Colors.grey),
                    const SizedBox(width: 4),
                    Text(
                      restaurant.platformOrigin!,
                      style: const TextStyle(color: Colors.grey),
                    ),
                  ],
                ],
              ),

              const SizedBox(height: 12),

              // Rating and orders
              Row(
                children: [
                  if (restaurant.avgRating != null) ...[
                    const Icon(Icons.star, size: 20, color: Colors.amber),
                    const SizedBox(width: 4),
                    Text(
                      restaurant.avgRating!.toStringAsFixed(1),
                      style: const TextStyle(
                        fontSize: 16,
                        fontWeight: FontWeight.w600,
                      ),
                    ),
                    const SizedBox(width: 16),
                  ],
                  const Icon(Icons.shopping_bag_outlined,
                      size: 18, color: Colors.grey),
                  const SizedBox(width: 4),
                  Text(
                    '${restaurant.totalOrders} sipariş',
                    style: const TextStyle(color: Colors.grey),
                  ),
                ],
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildRiskBadge(RiskStatus status) {
    Color color;
    String label;
    IconData icon;

    switch (status) {
      case RiskStatus.safe:
        color = Colors.green;
        label = 'Güvenli';
        icon = Icons.check_circle;
        break;
      case RiskStatus.watchlist:
        color = Colors.orange;
        label = 'Takipte';
        icon = Icons.warning;
        break;
      case RiskStatus.redFlag:
        color = Colors.red;
        label = 'Riskli';
        icon = Icons.flag;
        break;
      case RiskStatus.blacklisted:
        color = Colors.black;
        label = 'Kara Liste';
        icon = Icons.block;
        break;
    }

    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
      decoration: BoxDecoration(
        color: color.withOpacity(0.1),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: color),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(icon, size: 14, color: color),
          const SizedBox(width: 4),
          Text(
            label,
            style: TextStyle(
              color: color,
              fontSize: 12,
              fontWeight: FontWeight.bold,
            ),
          ),
        ],
      ),
    );
  }
}
