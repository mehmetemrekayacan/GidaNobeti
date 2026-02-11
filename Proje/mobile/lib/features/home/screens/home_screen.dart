import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import '../../../core/api/services/restaurant_api_service.dart';
import '../../../core/api/models/restaurant_models.dart';
import '../../auth/bloc/auth_bloc.dart';
import '../../restaurant/screens/restaurant_detail_screen.dart';

class HomeScreen extends StatelessWidget {
  const HomeScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Gıda Nöbeti'),
        backgroundColor: Colors.orange,
        foregroundColor: Colors.white,
        actions: [
          IconButton(
            icon: const Icon(Icons.logout),
            onPressed: () {
              _showLogoutDialog(context);
            },
          ),
        ],
      ),
      body: BlocListener<AuthBloc, AuthState>(
        listener: (context, state) {
          if (state is AuthUnauthenticated) {
            // Navigate to login screen after logout
            Navigator.pushReplacementNamed(context, '/login');
          }
        },
        child: BlocBuilder<AuthBloc, AuthState>(
          builder: (context, state) {
            if (state is AuthAuthenticated) {
              return _buildHomeContent(context, state);
            }

            return const Center(
              child: CircularProgressIndicator(),
            );
          },
        ),
      ),
    );
  }

  Widget _buildHomeContent(BuildContext context, AuthAuthenticated state) {
    final user = state.user;

    return SingleChildScrollView(
      padding: const EdgeInsets.all(16.0),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          // Welcome Card
          Card(
            elevation: 4,
            child: Padding(
              padding: const EdgeInsets.all(16.0),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    children: [
                      CircleAvatar(
                        radius: 30,
                        backgroundColor: Colors.orange,
                        child: Text(
                          user.fullName[0].toUpperCase(),
                          style: const TextStyle(
                            fontSize: 24,
                            fontWeight: FontWeight.bold,
                            color: Colors.white,
                          ),
                        ),
                      ),
                      const SizedBox(width: 16),
                      Expanded(
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Text(
                              'Hoş Geldin,',
                              style: TextStyle(
                                fontSize: 14,
                                color: Colors.grey[600],
                              ),
                            ),
                            Text(
                              user.fullName,
                              style: const TextStyle(
                                fontSize: 20,
                                fontWeight: FontWeight.bold,
                              ),
                            ),
                          ],
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 16),
                  _buildInfoRow(Icons.badge, 'Rol', _getRoleName(user.role)),
                  if (user.roomNumber != null)
                    _buildInfoRow(Icons.home, 'Oda', user.roomNumber!),
                  if (user.email != null)
                    _buildInfoRow(Icons.email, 'E-posta', user.email!),
                  _buildInfoRow(
                    user.isVerified ? Icons.verified : Icons.pending,
                    'Durum',
                    user.isVerified ? 'Onaylandı' : 'Onay Bekliyor',
                  ),
                ],
              ),
            ),
          ),
          const SizedBox(height: 24),

          // Risk Panosu - Riskli Restoranlar
          const Text(
            'Risk Panosu',
            style: TextStyle(
              fontSize: 18,
              fontWeight: FontWeight.bold,
            ),
          ),
          const SizedBox(height: 8),
          FutureBuilder<List<Restaurant>>(
            future: RestaurantApiService().getRiskyRestaurants(),
            builder: (context, snapshot) {
              if (snapshot.connectionState == ConnectionState.waiting) {
                return const Card(
                  child: Padding(
                    padding: EdgeInsets.all(24.0),
                    child: Center(child: CircularProgressIndicator()),
                  ),
                );
              }
              if (snapshot.hasError) {
                return Card(
                  child: Padding(
                    padding: const EdgeInsets.all(16.0),
                    child: Text(
                      'Riskli restoranlar yüklenemedi: ${snapshot.error}',
                      style: TextStyle(color: Colors.red[700]),
                    ),
                  ),
                );
              }
              final list = snapshot.data ?? [];
              if (list.isEmpty) {
                return Card(
                  child: Padding(
                    padding: const EdgeInsets.all(16.0),
                    child: Text(
                      'Şu an riskli restoran bulunmuyor.',
                      style: TextStyle(color: Colors.grey[600]),
                    ),
                  ),
                );
              }
              return Card(
                child: Column(
                  children: [
                    ...list.take(5).map((r) => ListTile(
                      leading: CircleAvatar(
                        backgroundColor: _riskColor(r.riskStatus),
                        child: Icon(Icons.warning_amber, color: Colors.white, size: 20),
                      ),
                      title: Text(r.name),
                      subtitle: Text(_riskLabel(r.riskStatus)),
                      onTap: () {
                        Navigator.push(
                          context,
                          MaterialPageRoute(
                            builder: (context) => RestaurantDetailScreen(restaurantId: r.id),
                          ),
                        );
                      },
                    )),
                    if (list.length > 5)
                      TextButton(
                        onPressed: () => Navigator.pushNamed(context, '/risky-restaurants'),
                        child: const Text('Tümünü gör'),
                      ),
                  ],
                ),
              );
            },
          ),
          const SizedBox(height: 24),

          // Quick Actions
          const Text(
            'Hızlı İşlemler',
            style: TextStyle(
              fontSize: 18,
              fontWeight: FontWeight.bold,
            ),
          ),
          const SizedBox(height: 12),

          GridView.count(
            crossAxisCount: 2,
            shrinkWrap: true,
            physics: const NeverScrollableScrollPhysics(),
            mainAxisSpacing: 12,
            crossAxisSpacing: 12,
            children: [
              _buildQuickActionCard(
                context,
                icon: Icons.restaurant_menu,
                title: 'Restoranlar',
                color: Colors.green,
                onTap: () {
                  Navigator.pushNamed(context, '/restaurants');
                },
              ),
              _buildQuickActionCard(
                context,
                icon: Icons.restaurant,
                title: 'Riskli Restoranlar',
                color: Colors.red,
                onTap: () => Navigator.pushNamed(context, '/risky-restaurants'),
              ),
              _buildQuickActionCard(
                context,
                icon: Icons.upload_file,
                title: 'Sipariş Yükle',
                color: Colors.blue,
                onTap: () => Navigator.pushNamed(context, '/order-upload'),
              ),
              _buildQuickActionCard(
                context,
                icon: Icons.history,
                title: 'Geçmiş',
                color: Colors.green,
                onTap: () => Navigator.pushNamed(context, '/order-history'),
              ),
              _buildQuickActionCard(
                context,
                icon: Icons.settings,
                title: 'Ayarlar',
                color: Colors.grey,
                onTap: () {
                  ScaffoldMessenger.of(context).showSnackBar(
                    const SnackBar(content: Text('Yakında...')),
                  );
                },
              ),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildInfoRow(IconData icon, String label, String value) {
    return Padding(
      padding: const EdgeInsets.only(top: 8.0),
      child: Row(
        children: [
          Icon(icon, size: 16, color: Colors.grey[600]),
          const SizedBox(width: 8),
          Text(
            '$label: ',
            style: TextStyle(
              fontSize: 14,
              color: Colors.grey[600],
            ),
          ),
          Text(
            value,
            style: const TextStyle(
              fontSize: 14,
              fontWeight: FontWeight.w500,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildQuickActionCard(
    BuildContext context, {
    required IconData icon,
    required String title,
    required Color color,
    required VoidCallback onTap,
  }) {
    return Card(
      elevation: 2,
      child: InkWell(
        onTap: onTap,
        borderRadius: BorderRadius.circular(8),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(icon, size: 48, color: color),
            const SizedBox(height: 8),
            Text(
              title,
              textAlign: TextAlign.center,
              style: const TextStyle(
                fontSize: 14,
                fontWeight: FontWeight.w500,
              ),
            ),
          ],
        ),
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

  String _getRoleName(dynamic role) {
    final roleStr = role.toString().split('.').last;
    switch (roleStr) {
      case 'student':
        return 'Öğrenci';
      case 'dormManager':
        return 'Yurt Müdürü';
      case 'security':
        return 'Güvenlik';
      case 'sysAdmin':
        return 'Sistem Yöneticisi';
      default:
        return roleStr;
    }
  }

  void _showLogoutDialog(BuildContext context) {
    showDialog(
      context: context,
      builder: (BuildContext dialogContext) {
        return AlertDialog(
          title: const Text('Çıkış Yap'),
          content: const Text('Çıkış yapmak istediğinize emin misiniz?'),
          actions: [
            TextButton(
              onPressed: () {
                Navigator.of(dialogContext).pop();
              },
              child: const Text('İptal'),
            ),
            TextButton(
              onPressed: () {
                Navigator.of(dialogContext).pop();
                context.read<AuthBloc>().add(const AuthLogoutRequested());
              },
              style: TextButton.styleFrom(foregroundColor: Colors.red),
              child: const Text('Çıkış Yap'),
            ),
          ],
        );
      },
    );
  }
}
