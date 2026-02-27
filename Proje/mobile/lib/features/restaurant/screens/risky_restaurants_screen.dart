import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:intl/intl.dart';
import '../../../core/api/models/restaurant_models.dart';
import '../../../core/api/services/restaurant_api_service.dart';
import '../../../core/router/app_routes.dart';

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
  final DateFormat _dateFormat = DateFormat('dd.MM.yyyy HH:mm');

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
                child: Center(
                  child: Padding(
                    padding: const EdgeInsets.symmetric(horizontal: 28),
                    child: Column(
                      mainAxisSize: MainAxisSize.min,
                      children: [
                        Icon(
                          Icons.check_circle,
                          size: 72,
                          color: Colors.green.shade600,
                        ),
                        const SizedBox(height: 16),
                        const Text(
                          'Şu an yurdunuzun çevresinde riskli olarak işaretlenmiş restoran bulunmamaktadır. Güvenle sipariş verebilirsiniz.',
                          textAlign: TextAlign.center,
                          style: TextStyle(fontSize: 15),
                        ),
                      ],
                    ),
                  ),
                ),
              );
            }
            return ListView.builder(
              padding: const EdgeInsets.fromLTRB(12, 12, 12, 24),
              itemCount: list.length,
              itemBuilder: (context, index) {
                final r = list[index];
                final visual = _riskVisual(r.riskStatus);
                final updatedText = r.riskUpdatedAt != null
                    ? _dateFormat.format(r.riskUpdatedAt!.toLocal())
                    : 'Bilinmiyor';

                return Card(
                  margin: const EdgeInsets.symmetric(vertical: 6),
                  elevation: 0,
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(16),
                    side: BorderSide(color: visual.borderColor, width: 1.5),
                  ),
                  child: InkWell(
                    borderRadius: BorderRadius.circular(16),
                    onTap: () {
                      context.pushNamed(
                        AppRoutes.restaurantDetailName,
                        pathParameters: AppRoutes.restaurantDetailParameters(r.id),
                      );
                    },
                    child: Padding(
                      padding: const EdgeInsets.all(14),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Row(
                            children: [
                              Icon(Icons.warning_amber_rounded,
                                  color: visual.iconColor, size: 22),
                              const SizedBox(width: 8),
                              Expanded(
                                child: Text(
                                  r.name,
                                  style: const TextStyle(
                                    fontSize: 16,
                                    fontWeight: FontWeight.w700,
                                  ),
                                ),
                              ),
                              Container(
                                padding: const EdgeInsets.symmetric(
                                    horizontal: 10, vertical: 5),
                                decoration: BoxDecoration(
                                  color: visual.badgeBg,
                                  borderRadius: BorderRadius.circular(999),
                                ),
                                child: Text(
                                  _riskLabel(r.riskStatus),
                                  style: TextStyle(
                                    fontSize: 12,
                                    fontWeight: FontWeight.w700,
                                    color: visual.badgeText,
                                  ),
                                ),
                              ),
                            ],
                          ),
                          const SizedBox(height: 10),
                          Text(
                            'Risk sebebi: ${r.riskReason?.trim().isNotEmpty == true ? r.riskReason! : 'Belirtilmemiş'}',
                            style: TextStyle(
                              color: Colors.grey.shade800,
                              height: 1.3,
                            ),
                          ),
                          const SizedBox(height: 8),
                          Text(
                            'Son güncelleme: $updatedText',
                            style: TextStyle(
                              color: Colors.grey.shade700,
                              fontSize: 13,
                            ),
                          ),
                        ],
                      ),
                    ),
                  ),
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

  _RiskVisual _riskVisual(RiskStatus status) {
    switch (status) {
      case RiskStatus.redFlag:
      case RiskStatus.blacklisted:
        return _RiskVisual(
          borderColor: Colors.red.shade200,
          iconColor: Colors.red.shade700,
          badgeBg: Colors.red.shade100,
          badgeText: Colors.red.shade800,
        );
      case RiskStatus.watchlist:
        return _RiskVisual(
          borderColor: Colors.orange.shade200,
          iconColor: Colors.orange.shade800,
          badgeBg: Colors.orange.shade100,
          badgeText: Colors.orange.shade900,
        );
      default:
        return _RiskVisual(
          borderColor: Colors.grey.shade300,
          iconColor: Colors.grey.shade700,
          badgeBg: Colors.grey.shade200,
          badgeText: Colors.grey.shade800,
        );
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

class _RiskVisual {
  final Color borderColor;
  final Color iconColor;
  final Color badgeBg;
  final Color badgeText;

  _RiskVisual({
    required this.borderColor,
    required this.iconColor,
    required this.badgeBg,
    required this.badgeText,
  });
}
