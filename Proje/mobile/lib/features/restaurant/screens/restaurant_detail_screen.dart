import 'package:flutter/material.dart';
import '../../../core/api/models/restaurant_models.dart';
import '../../../core/api/services/restaurant_api_service.dart';

class RestaurantDetailScreen extends StatefulWidget {
  final int restaurantId;

  const RestaurantDetailScreen({
    super.key,
    required this.restaurantId,
  });

  @override
  State<RestaurantDetailScreen> createState() => _RestaurantDetailScreenState();
}

class _RestaurantDetailScreenState extends State<RestaurantDetailScreen> {
  final _apiService = RestaurantApiService();
  Restaurant? _restaurant;
  bool _isLoading = true;
  String? _errorMessage;

  @override
  void initState() {
    super.initState();
    _loadRestaurant();
  }

  Future<void> _loadRestaurant() async {
    setState(() {
      _isLoading = true;
      _errorMessage = null;
    });

    try {
      final restaurant = await _apiService.getRestaurant(widget.restaurantId);
      setState(() {
        _restaurant = restaurant;
        _isLoading = false;
      });
    } catch (e) {
      setState(() {
        _errorMessage = e.toString();
        _isLoading = false;
      });
    }
  }

  Color _getRiskColor(RiskStatus status) {
    switch (status) {
      case RiskStatus.safe:
        return Colors.green;
      case RiskStatus.watchlist:
        return Colors.orange;
      case RiskStatus.redFlag:
        return Colors.red;
      case RiskStatus.blacklisted:
        return Colors.black;
    }
  }

  String _getRiskLabel(RiskStatus status) {
    switch (status) {
      case RiskStatus.safe:
        return 'Güvenli';
      case RiskStatus.watchlist:
        return 'İzleme Listesi';
      case RiskStatus.redFlag:
        return 'Riskli';
      case RiskStatus.blacklisted:
        return 'Kara Liste';
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text(_restaurant?.name ?? 'Restoran Detayı'),
      ),
      body: _isLoading
          ? const Center(child: CircularProgressIndicator())
          : _errorMessage != null
              ? Center(
                  child: Column(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      const Icon(Icons.error_outline, size: 64, color: Colors.red),
                      const SizedBox(height: 16),
                      Text(_errorMessage!),
                      const SizedBox(height: 16),
                      ElevatedButton(
                        onPressed: _loadRestaurant,
                        child: const Text('Tekrar Dene'),
                      ),
                    ],
                  ),
                )
              : _restaurant == null
                  ? const Center(child: Text('Restoran bulunamadı'))
                  : SingleChildScrollView(
                      padding: const EdgeInsets.all(16.0),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          // Risk Badge
                          Container(
                            padding: const EdgeInsets.symmetric(
                              horizontal: 12,
                              vertical: 6,
                            ),
                            decoration: BoxDecoration(
                              color: _getRiskColor(_restaurant!.riskStatus),
                              borderRadius: BorderRadius.circular(16),
                            ),
                            child: Text(
                              _getRiskLabel(_restaurant!.riskStatus),
                              style: const TextStyle(
                                color: Colors.white,
                                fontWeight: FontWeight.bold,
                              ),
                            ),
                          ),
                          const SizedBox(height: 24),

                          // Name
                          Text(
                            _restaurant!.name,
                            style: Theme.of(context).textTheme.headlineMedium,
                          ),
                          const SizedBox(height: 16),

                          // Rating
                          Row(
                            children: [
                              const Icon(Icons.star, color: Colors.amber, size: 20),
                              const SizedBox(width: 4),
                              Text(
                                _restaurant!.avgRating?.toStringAsFixed(1) ?? 'N/A',
                                style: const TextStyle(
                                  fontSize: 18,
                                  fontWeight: FontWeight.bold,
                                ),
                              ),
                            ],
                          ),
                          const SizedBox(height: 24),

                          // Info Cards
                          _buildInfoCard(
                            icon: Icons.location_on,
                            label: 'Bölge',
                            value: _restaurant!.district ?? 'Belirtilmemiş',
                          ),
                          const SizedBox(height: 12),
                          _buildInfoCard(
                            icon: Icons.shopping_bag,
                            label: 'Platform',
                            value: _restaurant!.platformOrigin ?? 'Belirtilmemiş',
                          ),
                          const SizedBox(height: 12),
                          _buildInfoCard(
                            icon: Icons.receipt_long,
                            label: 'Toplam Sipariş',
                            value: '${_restaurant!.totalOrders}',
                          ),
                          const SizedBox(height: 12),
                          _buildInfoCard(
                            icon: _restaurant!.isActive
                                ? Icons.check_circle
                                : Icons.cancel,
                            label: 'Durum',
                            value: _restaurant!.isActive ? 'Aktif' : 'Pasif',
                            valueColor: _restaurant!.isActive
                                ? Colors.green
                                : Colors.grey,
                          ),
                        ],
                      ),
                    ),
    );
  }

  Widget _buildInfoCard({
    required IconData icon,
    required String label,
    required String value,
    Color? valueColor,
  }) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.grey[100],
        borderRadius: BorderRadius.circular(12),
      ),
      child: Row(
        children: [
          Icon(icon, color: Colors.blue),
          const SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  label,
                  style: const TextStyle(
                    fontSize: 12,
                    color: Colors.grey,
                  ),
                ),
                const SizedBox(height: 4),
                Text(
                  value,
                  style: TextStyle(
                    fontSize: 16,
                    fontWeight: FontWeight.w600,
                    color: valueColor,
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}
