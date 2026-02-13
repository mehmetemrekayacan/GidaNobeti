import 'package:flutter/material.dart';
import '../../../core/api/models/restaurant_models.dart';
import '../../../core/api/services/restaurant_api_service.dart';
import 'restaurant_detail_screen.dart';

/// Full-screen list of risky restaurants (Risk Panosu).
/// Pull-to-refresh ile admin’de yapılan risk değişiklikleri anında yansır.
class RiskyRestaurantsScreen extends StatefulWidget {
  const RiskyRestaurantsScreen({super.key});

  @override
  State<RiskyRestaurantsScreen> createState() => _RiskyRestaurantsScreenState();
}

class _RiskyRestaurantsScreenState extends State<RiskyRestaurantsScreen> {
  final RestaurantApiService _api = RestaurantApiService();
  late Future<List<Restaurant>> _future;

  @override
  void initState() {
    super.initState();
    _future = _api.getRiskyRestaurants();
  }

  Future<void> _onRefresh() async {
    setState(() {
      _future = _api.getRiskyRestaurants();
    });
    await _future;
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Riskli Restoranlar'),
        backgroundColor: Colors.orange,
        foregroundColor: Colors.white,
      ),
      body: RefreshIndicator(
        onRefresh: _onRefresh,
        child: FutureBuilder<List<Restaurant>>(
          future: _future,
          builder: (context, snapshot) {
            if (snapshot.connectionState == ConnectionState.waiting) {
              return const Center(child: CircularProgressIndicator());
            }
            if (snapshot.hasError) {
              return _buildScrollable(
                child: Center(
                  child: Padding(
                    padding: const EdgeInsets.all(24.0),
                    child: Text(
                      'Yüklenemedi: ${snapshot.error}',
                      style: TextStyle(color: Colors.red[700]),
                      textAlign: TextAlign.center,
                    ),
                  ),
                ),
              );
            }
            final list = snapshot.data ?? [];
            if (list.isEmpty) {
              return _buildScrollable(
                child: const Center(
                  child: Padding(
                    padding: EdgeInsets.all(24.0),
                    child: Text('Riskli restoran bulunmuyor.'),
                  ),
                ),
              );
            }
            return ListView.builder(
              padding: const EdgeInsets.only(bottom: 24),
              itemCount: list.length,
              itemBuilder: (context, index) {
                final r = list[index];
                final color = _riskColor(r.riskStatus);
                return ListTile(
                  leading: CircleAvatar(
                    backgroundColor: color,
                    child: const Icon(
                      Icons.warning_amber,
                      color: Colors.white,
                      size: 22,
                    ),
                  ),
                  title: Text(r.name),
                  subtitle: Text(_riskLabel(r.riskStatus)),
                  trailing: const Icon(Icons.chevron_right),
                  onTap: () {
                    Navigator.push(
                      context,
                      MaterialPageRoute(
                        builder: (context) =>
                            RestaurantDetailScreen(restaurantId: r.id),
                      ),
                    );
                  },
                );
              },
            );
          },
        ),
      ),
    );
  }

  /// RefreshIndicator için kısa içerikte de kaydırılabilir alan (pull çalışsın diye).
  Widget _buildScrollable({required Widget child}) {
    return SingleChildScrollView(
      physics: const AlwaysScrollableScrollPhysics(),
      child: SizedBox(
        height: MediaQuery.of(context).size.height * 0.6,
        child: child,
      ),
    );
  }

  Color _riskColor(RiskStatus status) {
    switch (status) {
      case RiskStatus.redFlag:
      case RiskStatus.blacklisted:
        return Colors.red;
      case RiskStatus.watchlist:
        return Colors.orange;
      default:
        return Colors.grey;
    }
  }

  String _riskLabel(RiskStatus status) {
    switch (status) {
      case RiskStatus.redFlag:
        return 'Yüksek risk';
      case RiskStatus.blacklisted:
        return 'Yasaklı';
      case RiskStatus.watchlist:
        return 'İzleme listesinde';
      default:
        return 'Bilgi yok';
    }
  }
}
