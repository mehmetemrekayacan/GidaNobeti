import 'package:flutter/material.dart';
import '../../../core/api/models/restaurant_models.dart';
import '../../../core/api/services/restaurant_api_service.dart';
import 'restaurant_detail_screen.dart';

/// Full-screen list of risky restaurants (Risk Panosu)
class RiskyRestaurantsScreen extends StatelessWidget {
  const RiskyRestaurantsScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Riskli Restoranlar'),
        backgroundColor: Colors.orange,
        foregroundColor: Colors.white,
      ),
      body: FutureBuilder<List<Restaurant>>(
        future: RestaurantApiService().getRiskyRestaurants(),
        builder: (context, snapshot) {
          if (snapshot.connectionState == ConnectionState.waiting) {
            return const Center(child: CircularProgressIndicator());
          }
          if (snapshot.hasError) {
            return Center(
              child: Padding(
                padding: const EdgeInsets.all(24.0),
                child: Text(
                  'Yüklenemedi: ${snapshot.error}',
                  style: TextStyle(color: Colors.red[700]),
                  textAlign: TextAlign.center,
                ),
              ),
            );
          }
          final list = snapshot.data ?? [];
          if (list.isEmpty) {
            return const Center(
              child: Text('Riskli restoran bulunmuyor.'),
            );
          }
          return ListView.builder(
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
