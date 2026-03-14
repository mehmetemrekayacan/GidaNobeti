import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:go_router/go_router.dart';
import 'package:intl/intl.dart';

import '../../../core/api/models/restaurant_models.dart';
import '../../../core/router/app_routes.dart';
import '../../auth/bloc/auth_bloc.dart';
import '../../order/bloc/order_bloc.dart';
import '../../order/bloc/order_event.dart';
import '../../order/bloc/order_state.dart';
import '../../restaurant/bloc/restaurant_bloc.dart';

class HomeScreen extends StatelessWidget {
  const HomeScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return MultiBlocProvider(
      providers: [
        BlocProvider<OrderBloc>(
          create: (_) => OrderBloc(),
        ),
        BlocProvider<RestaurantBloc>(
          create: (_) => RestaurantBloc(),
        ),
      ],
      child: const _HomeDashboardScreen(),
    );
  }
}

class _HomeDashboardScreen extends StatefulWidget {
  const _HomeDashboardScreen();

  @override
  State<_HomeDashboardScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<_HomeDashboardScreen> {
  final NumberFormat _currencyFormat = NumberFormat.currency(
    locale: 'tr_TR',
    symbol: 'TL ',
    decimalDigits: 2,
  );
  final DateFormat _dateFormat = DateFormat('d MMM, HH:mm', 'tr_TR');

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      if (!mounted) return;
      _fetchDashboardData(refresh: true);
    });
  }

  void _fetchDashboardData({required bool refresh}) {
    final authBloc = context.read<AuthBloc>();
    if (authBloc.state is! AuthAuthenticated && authBloc.state is! AuthLoading) {
      authBloc.add(const AuthCheckRequested());
    }

    context.read<OrderBloc>().add(
          OrderHistoryRequested(
            page: 1,
            limit: 3,
            refresh: true,
          ),
        );

    context.read<RestaurantBloc>().add(
          refresh
              ? const RestaurantRefreshRequested()
              : const RestaurantLoadRequested(),
        );
  }

  Future<void> _onRefresh() async {
    _fetchDashboardData(refresh: true);
    await Future.wait<void>([
      _waitForOrderHistoryLoad(),
      _waitForRestaurantLoad(),
    ]);
  }

  Future<void> _waitForOrderHistoryLoad() async {
    final bloc = context.read<OrderBloc>();
    if (!bloc.state.isHistoryLoading) return;

    await bloc.stream
        .firstWhere((state) => !state.isHistoryLoading)
        .timeout(const Duration(seconds: 6), onTimeout: () => bloc.state);
  }

  Future<void> _waitForRestaurantLoad() async {
    final bloc = context.read<RestaurantBloc>();
    final state = bloc.state;

    if (state is RestaurantLoaded || state is RestaurantError) {
      return;
    }

    await bloc.stream
        .firstWhere(
          (nextState) =>
              nextState is RestaurantLoaded || nextState is RestaurantError,
        )
        .timeout(const Duration(seconds: 6), onTimeout: () => bloc.state);
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFFF6F8FC),
      body: BlocListener<AuthBloc, AuthState>(
        listener: (context, state) {
          if (state is AuthUnauthenticated) {
            context.goNamed(AppRoutes.loginName);
          }
        },
        child: SafeArea(
          child: RefreshIndicator(
            color: const Color(0xFF0F766E),
            onRefresh: _onRefresh,
            child: SingleChildScrollView(
              physics: const AlwaysScrollableScrollPhysics(),
              padding: const EdgeInsets.fromLTRB(18, 12, 18, 24),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  _buildTopHeader(),
                  const SizedBox(height: 24),
                  _buildQuickActions(),
                  const SizedBox(height: 22),
                  _buildRiskRadar(),
                  const SizedBox(height: 22),
                  _buildRecentOrders(),
                ],
              ),
            ),
          ),
        ),
      ),
    );
  }

  Widget _buildTopHeader() {
    return BlocBuilder<AuthBloc, AuthState>(
      builder: (context, authState) {
        final isAuthenticated = authState is AuthAuthenticated;
        final userName = isAuthenticated
            ? authState.user.fullName.split(' ').first
            : 'Kullanıcı';
        final avatarText = isAuthenticated && authState.user.fullName.isNotEmpty
            ? authState.user.fullName.trim()[0].toUpperCase()
            : 'G';

        return Container(
          decoration: BoxDecoration(
            gradient: const LinearGradient(
              colors: [Color(0xFF0F766E), Color(0xFF115E59)],
              begin: Alignment.topLeft,
              end: Alignment.bottomRight,
            ),
            borderRadius: BorderRadius.circular(24),
            boxShadow: [
              BoxShadow(
                color: const Color(0xFF0F766E).withValues(alpha: 0.25),
                blurRadius: 24,
                offset: const Offset(0, 10),
              ),
            ],
          ),
          child: Padding(
            padding: const EdgeInsets.symmetric(horizontal: 18, vertical: 18),
            child: Row(
              children: [
                Expanded(
                  child: isAuthenticated
                      ? Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Text(
                              'Merhaba, $userName 👋',
                              style: const TextStyle(
                                color: Colors.white,
                                fontSize: 23,
                                fontWeight: FontWeight.w800,
                              ),
                            ),
                            const SizedBox(height: 8),
                            Text(
                              'Bugün neler oluyor, birlikte gözden geçirelim.',
                              style: TextStyle(
                                color: Colors.white.withValues(alpha: 0.9),
                                fontSize: 13,
                                height: 1.3,
                              ),
                            ),
                          ],
                        )
                      : const Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            _ShimmerBox(width: 170, height: 24, radius: 10),
                            SizedBox(height: 10),
                            _ShimmerBox(width: 220, height: 14, radius: 8),
                          ],
                        ),
                ),
                const SizedBox(width: 12),
                GestureDetector(
                  onTap: () => context.pushNamed(AppRoutes.profileName),
                  child: CircleAvatar(
                    radius: 25,
                    backgroundColor: Colors.white,
                    child: Text(
                      avatarText,
                      style: const TextStyle(
                        color: Color(0xFF0F766E),
                        fontWeight: FontWeight.bold,
                        fontSize: 20,
                      ),
                    ),
                  ),
                ),
                PopupMenuButton<String>(
                  iconColor: Colors.white,
                  onSelected: (value) {
                    if (value == 'logout') {
                      _showLogoutDialog(context);
                    }
                    if (value == 'profile') {
                      context.pushNamed(AppRoutes.profileName);
                    }
                  },
                  itemBuilder: (context) => const [
                    PopupMenuItem<String>(
                      value: 'profile',
                      child: Text('Profilim'),
                    ),
                    PopupMenuItem<String>(
                      value: 'logout',
                      child: Text('Çıkış Yap'),
                    ),
                  ],
                ),
              ],
            ),
          ),
        );
      },
    );
  }

  Widget _buildQuickActions() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const _SectionTitle(
          title: 'Hızlı İşlemler',
          subtitle: 'Tek dokunuşla en sık kullandığın alanlar',
        ),
        const SizedBox(height: 12),
        Row(
          children: [
            Expanded(
              child: _QuickActionCard(
                title: 'Fiş Okut',
                subtitle: 'OCR ile yeni sipariş ekle',
                icon: Icons.document_scanner_rounded,
                onTap: () => context.pushNamed(AppRoutes.orderUploadName),
                gradient: const [Color(0xFF1D4ED8), Color(0xFF0EA5E9)],
              ),
            ),
            const SizedBox(width: 12),
            Expanded(
              child: _QuickActionCard(
                title: 'Bildirimlerim',
                subtitle: 'Sağlık bildirimlerini takip et',
                icon: Icons.notifications_active_rounded,
                onTap: () => context.pushNamed(AppRoutes.myIncidentsName),
                gradient: const [Color(0xFF059669), Color(0xFF10B981)],
              ),
            ),
          ],
        ),
      ],
    );
  }

  Widget _buildRiskRadar() {
    return BlocBuilder<RestaurantBloc, RestaurantState>(
      builder: (context, restaurantState) {
        final riskyRestaurants = _extractRiskyRestaurants(restaurantState);

        return Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const _SectionTitle(
              title: 'Dikkat Çeken Restoranlar',
              subtitle: 'WATCHLIST ve RED_FLAG durumundaki yerler',
            ),
            const SizedBox(height: 12),
            if (restaurantState is RestaurantLoading ||
                restaurantState is RestaurantInitial)
              const _RiskRadarSkeleton()
            else if (restaurantState is RestaurantError)
              _ErrorCard(
                message: 'Risk verisi alınamadı. Lütfen tekrar yenileyin.',
                onRetry: () => context
                    .read<RestaurantBloc>()
                    .add(const RestaurantLoadRequested()),
              )
            else if (riskyRestaurants.isEmpty)
              _RiskEmptyState(
                onExplore: () => context.pushNamed(AppRoutes.restaurantListName),
              )
            else
              SizedBox(
                height: 168,
                child: ListView.separated(
                  scrollDirection: Axis.horizontal,
                  itemCount: riskyRestaurants.length,
                  separatorBuilder: (context, index) => const SizedBox(width: 12),
                  itemBuilder: (context, index) {
                    final restaurant = riskyRestaurants[index];
                    return _RiskRestaurantCard(
                      restaurant: restaurant,
                      onTap: () => context.pushNamed(
                        AppRoutes.restaurantDetailName,
                        pathParameters:
                            AppRoutes.restaurantDetailParameters(restaurant.id),
                      ),
                    );
                  },
                ),
              ),
          ],
        );
      },
    );
  }

  Widget _buildRecentOrders() {
    return BlocBuilder<OrderBloc, OrderState>(
      builder: (context, orderState) {
        final recentOrders = orderState.historyItems.take(3).toList();

        return Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const _SectionTitle(
              title: 'Son Siparişler',
              subtitle: 'En son 3 siparişin ve hızlı şikâyet butonu',
            ),
            const SizedBox(height: 12),
            if (orderState.isHistoryLoading && recentOrders.isEmpty)
              const _RecentOrderSkeleton()
            else if (orderState.historyError != null && recentOrders.isEmpty)
              _ErrorCard(
                message: orderState.historyError!,
                onRetry: () => context.read<OrderBloc>().add(
                      const OrderHistoryRequested(
                        page: 1,
                        limit: 3,
                        refresh: true,
                      ),
                    ),
              )
            else if (recentOrders.isEmpty)
              _EmptyCard(
                title: 'Henüz sipariş bulunmuyor',
                subtitle: 'İlk fişini okutup sipariş geçmişini oluşturabilirsin.',
                icon: Icons.receipt_long_rounded,
              )
            else
              Column(
                children: recentOrders
                    .map(
                      (order) => Padding(
                        padding: const EdgeInsets.only(bottom: 10),
                        child: _OrderCard(
                          restaurantName: order.restaurant?.name ?? 'Bilinmeyen restoran',
                          dateText: _dateFormat.format(order.declaredAt),
                          amountText: order.totalAmount == null
                              ? 'Tutar belirtilmedi'
                              : _currencyFormat.format(order.totalAmount),
                          riskStatus: order.restaurant?.currentRiskStatus,
                          onComplain: () =>
                              context.pushNamed(AppRoutes.incidentReportName),
                          onOpenHistory: () =>
                              context.pushNamed(AppRoutes.orderHistoryName),
                        ),
                      ),
                    )
                    .toList(),
              ),
          ],
        );
      },
    );
  }

  List<Restaurant> _extractRiskyRestaurants(RestaurantState state) {
    if (state is! RestaurantLoaded) return const [];

    final filtered = state.restaurants
        .where(
          (restaurant) => restaurant.riskStatus == RiskStatus.watchlist ||
              restaurant.riskStatus == RiskStatus.redFlag,
        )
        .toList();

    filtered.sort((a, b) {
      final rankA = a.riskStatus == RiskStatus.redFlag ? 0 : 1;
      final rankB = b.riskStatus == RiskStatus.redFlag ? 0 : 1;
      if (rankA != rankB) return rankA.compareTo(rankB);
      return a.name.compareTo(b.name);
    });

    return filtered.take(10).toList();
  }

  String _riskStatusLabel(RiskStatus status) {
    switch (status) {
      case RiskStatus.redFlag:
        return 'RED FLAG';
      case RiskStatus.watchlist:
        return 'WATCHLIST';
      case RiskStatus.blacklisted:
        return 'BLACKLISTED';
      case RiskStatus.safe:
        return 'SAFE';
    }
  }

  Color _riskStatusColor(RiskStatus status) {
    switch (status) {
      case RiskStatus.redFlag:
        return const Color(0xFFDC2626);
      case RiskStatus.watchlist:
        return const Color(0xFFD97706);
      case RiskStatus.blacklisted:
        return const Color(0xFF7F1D1D);
      case RiskStatus.safe:
        return const Color(0xFF10B981);
    }
  }

  Color _riskBadgeBackground(String? status) {
    switch (status) {
      case 'RED_FLAG':
        return const Color(0xFFFEE2E2);
      case 'WATCHLIST':
        return const Color(0xFFFFF7ED);
      case 'BLACKLISTED':
        return const Color(0xFFFECACA);
      default:
        return const Color(0xFFDCFCE7);
    }
  }

  Color _riskBadgeText(String? status) {
    switch (status) {
      case 'RED_FLAG':
        return const Color(0xFFB91C1C);
      case 'WATCHLIST':
        return const Color(0xFF9A3412);
      case 'BLACKLISTED':
        return const Color(0xFF7F1D1D);
      default:
        return const Color(0xFF166534);
    }
  }

  String _orderRiskLabel(String? status) {
    switch (status) {
      case 'RED_FLAG':
        return 'Riskli';
      case 'WATCHLIST':
        return 'İzlemede';
      case 'BLACKLISTED':
        return 'Yasaklı';
      default:
        return 'Güvenli';
    }
  }

  void _showLogoutDialog(BuildContext context) {
    showDialog(
      context: context,
      builder: (dialogContext) {
        return AlertDialog(
          title: const Text('Çıkış Yap'),
          content: const Text('Hesabınızdan çıkış yapmak istediğinize emin misiniz?'),
          actions: [
            TextButton(
              onPressed: () => Navigator.of(dialogContext).pop(),
              child: const Text('İptal'),
            ),
            FilledButton(
              style: FilledButton.styleFrom(
                backgroundColor: const Color(0xFFDC2626),
              ),
              onPressed: () {
                Navigator.of(dialogContext).pop();
                context.read<AuthBloc>().add(const AuthLogoutRequested());
              },
              child: const Text('Çıkış Yap'),
            ),
          ],
        );
      },
    );
  }
}

class _SectionTitle extends StatelessWidget {
  final String title;
  final String subtitle;

  const _SectionTitle({
    required this.title,
    required this.subtitle,
  });

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          title,
          style: const TextStyle(
            fontSize: 18,
            fontWeight: FontWeight.w800,
            color: Color(0xFF0F172A),
          ),
        ),
        const SizedBox(height: 3),
        Text(
          subtitle,
          style: const TextStyle(
            fontSize: 12,
            color: Color(0xFF64748B),
            fontWeight: FontWeight.w500,
          ),
        ),
      ],
    );
  }
}

class _QuickActionCard extends StatelessWidget {
  final String title;
  final String subtitle;
  final IconData icon;
  final VoidCallback onTap;
  final List<Color> gradient;

  const _QuickActionCard({
    required this.title,
    required this.subtitle,
    required this.icon,
    required this.onTap,
    required this.gradient,
  });

  @override
  Widget build(BuildContext context) {
    return Material(
      color: Colors.transparent,
      child: InkWell(
        onTap: onTap,
        borderRadius: BorderRadius.circular(20),
        child: Ink(
          height: 158,
          decoration: BoxDecoration(
            borderRadius: BorderRadius.circular(20),
            gradient: LinearGradient(
              colors: gradient,
              begin: Alignment.topLeft,
              end: Alignment.bottomRight,
            ),
            boxShadow: [
              BoxShadow(
                color: gradient.first.withValues(alpha: 0.3),
                blurRadius: 20,
                offset: const Offset(0, 8),
              ),
            ],
          ),
          child: Padding(
            padding: const EdgeInsets.all(14),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Container(
                  decoration: BoxDecoration(
                    color: Colors.white.withValues(alpha: 0.18),
                    borderRadius: BorderRadius.circular(12),
                  ),
                  padding: const EdgeInsets.all(9),
                  child: Icon(icon, color: Colors.white, size: 28),
                ),
                const Spacer(),
                Text(
                  title,
                  style: const TextStyle(
                    color: Colors.white,
                    fontSize: 17,
                    fontWeight: FontWeight.w800,
                  ),
                ),
                const SizedBox(height: 4),
                Text(
                  subtitle,
                  style: TextStyle(
                    color: Colors.white.withValues(alpha: 0.9),
                    fontSize: 12,
                    fontWeight: FontWeight.w500,
                  ),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }

}

class _RiskRestaurantCard extends StatelessWidget {
  final Restaurant restaurant;
  final VoidCallback onTap;

  const _RiskRestaurantCard({
    required this.restaurant,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    final homeState = context.findAncestorStateOfType<_HomeScreenState>();
    final statusColor = homeState?._riskStatusColor(restaurant.riskStatus) ??
        const Color(0xFFEF4444);
    final statusLabel = homeState?._riskStatusLabel(restaurant.riskStatus) ??
        restaurant.riskStatus.value;

    return GestureDetector(
      onTap: onTap,
      child: Container(
        width: 250,
        padding: const EdgeInsets.all(14),
        decoration: BoxDecoration(
          color: Colors.white,
          borderRadius: BorderRadius.circular(18),
          border: Border.all(color: const Color(0xFFE2E8F0)),
          boxShadow: const [
            BoxShadow(
              color: Color(0x1A334155),
              blurRadius: 16,
              offset: Offset(0, 7),
            ),
          ],
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Expanded(
                  child: Text(
                    restaurant.name,
                    maxLines: 2,
                    overflow: TextOverflow.ellipsis,
                    style: const TextStyle(
                      fontWeight: FontWeight.w700,
                      color: Color(0xFF0F172A),
                      fontSize: 15,
                    ),
                  ),
                ),
                const SizedBox(width: 8),
                Icon(Icons.radar_rounded, color: statusColor, size: 20),
              ],
            ),
            const SizedBox(height: 12),
            Container(
              decoration: BoxDecoration(
                color: statusColor.withValues(alpha: 0.12),
                borderRadius: BorderRadius.circular(100),
              ),
              padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
              child: Text(
                statusLabel,
                style: TextStyle(
                  color: statusColor,
                  fontWeight: FontWeight.w700,
                  fontSize: 12,
                ),
              ),
            ),
            const SizedBox(height: 10),
            Text(
              restaurant.district == null || restaurant.district!.isEmpty
                  ? 'Bolge bilgisi yok'
                  : restaurant.district!,
              style: const TextStyle(
                color: Color(0xFF475569),
                fontSize: 12,
              ),
            ),
            const Spacer(),
            Row(
              children: [
                const Icon(Icons.chevron_right_rounded,
                    size: 18, color: Color(0xFF94A3B8)),
                const SizedBox(width: 4),
                Text(
                  'Detayı aç',
                  style: TextStyle(
                    color: Colors.grey.shade700,
                    fontWeight: FontWeight.w600,
                    fontSize: 12,
                  ),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }
}

class _OrderCard extends StatelessWidget {
  final String restaurantName;
  final String dateText;
  final String amountText;
  final String? riskStatus;
  final VoidCallback onComplain;
  final VoidCallback onOpenHistory;

  const _OrderCard({
    required this.restaurantName,
    required this.dateText,
    required this.amountText,
    required this.riskStatus,
    required this.onComplain,
    required this.onOpenHistory,
  });

  @override
  Widget build(BuildContext context) {
    final homeState = context.findAncestorStateOfType<_HomeScreenState>();
    final badgeBg = homeState?._riskBadgeBackground(riskStatus) ??
        const Color(0xFFDCFCE7);
    final badgeText = homeState?._riskBadgeText(riskStatus) ??
        const Color(0xFF166534);
    final riskLabel = homeState?._orderRiskLabel(riskStatus) ?? 'Güvenli';

    return Container(
      width: double.infinity,
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: const Color(0xFFE2E8F0)),
      ),
      padding: const EdgeInsets.fromLTRB(14, 12, 14, 12),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Expanded(
                child: Text(
                  restaurantName,
                  style: const TextStyle(
                    fontSize: 15,
                    fontWeight: FontWeight.w700,
                    color: Color(0xFF0F172A),
                  ),
                ),
              ),
              Container(
                decoration: BoxDecoration(
                  color: badgeBg,
                  borderRadius: BorderRadius.circular(999),
                ),
                padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 5),
                child: Text(
                  riskLabel,
                  style: TextStyle(
                    color: badgeText,
                    fontWeight: FontWeight.w700,
                    fontSize: 11,
                  ),
                ),
              ),
            ],
          ),
          const SizedBox(height: 6),
          Text(
            dateText,
            style: const TextStyle(
              fontSize: 12,
              color: Color(0xFF64748B),
              fontWeight: FontWeight.w500,
            ),
          ),
          const SizedBox(height: 4),
          Text(
            amountText,
            style: const TextStyle(
              fontSize: 14,
              color: Color(0xFF1E293B),
              fontWeight: FontWeight.w700,
            ),
          ),
          const SizedBox(height: 10),
          Row(
            children: [
              Expanded(
                child: OutlinedButton.icon(
                  onPressed: onOpenHistory,
                  icon: const Icon(Icons.history_rounded, size: 16),
                  label: const Text('Geçmişe Git'),
                  style: OutlinedButton.styleFrom(
                    foregroundColor: const Color(0xFF334155),
                    side: const BorderSide(color: Color(0xFFCBD5E1)),
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(10),
                    ),
                  ),
                ),
              ),
              const SizedBox(width: 8),
              Expanded(
                child: FilledButton.icon(
                  onPressed: onComplain,
                  icon: const Icon(Icons.report_problem_rounded, size: 16),
                  label: const Text('Şikâyet Et'),
                  style: FilledButton.styleFrom(
                    backgroundColor: const Color(0xFFD97706),
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(10),
                    ),
                  ),
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }
}

class _RiskEmptyState extends StatelessWidget {
  final VoidCallback onExplore;

  const _RiskEmptyState({required this.onExplore});

  @override
  Widget build(BuildContext context) {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: const Color(0xFFECFDF5),
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: const Color(0xFFA7F3D0)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Row(
            children: [
              Icon(Icons.shield_moon_rounded, color: Color(0xFF047857)),
              SizedBox(width: 8),
              Expanded(
                child: Text(
                  'Şu an çevrendeki restoranlar güvenli',
                  style: TextStyle(
                    color: Color(0xFF065F46),
                    fontWeight: FontWeight.w700,
                    fontSize: 14,
                  ),
                ),
              ),
            ],
          ),
          const SizedBox(height: 8),
          Text(
            'Yine de tüm listeyi arada kontrol ederek güncel riskleri takip edebilirsin.',
            style: TextStyle(color: Colors.green.shade800, fontSize: 12),
          ),
          const SizedBox(height: 10),
          OutlinedButton(
            onPressed: onExplore,
            style: OutlinedButton.styleFrom(
              side: const BorderSide(color: Color(0xFF34D399)),
              foregroundColor: const Color(0xFF065F46),
            ),
            child: const Text('Restoran Listesini Aç'),
          ),
        ],
      ),
    );
  }
}

class _EmptyCard extends StatelessWidget {
  final String title;
  final String subtitle;
  final IconData icon;

  const _EmptyCard({
    required this.title,
    required this.subtitle,
    required this.icon,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: const Color(0xFFE2E8F0)),
      ),
      child: Row(
        children: [
          Container(
            width: 42,
            height: 42,
            decoration: BoxDecoration(
              color: const Color(0xFFE2E8F0),
              borderRadius: BorderRadius.circular(12),
            ),
            child: Icon(icon, color: const Color(0xFF475569)),
          ),
          const SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  title,
                  style: const TextStyle(
                    fontSize: 14,
                    fontWeight: FontWeight.w700,
                    color: Color(0xFF0F172A),
                  ),
                ),
                const SizedBox(height: 3),
                Text(
                  subtitle,
                  style: const TextStyle(
                    fontSize: 12,
                    color: Color(0xFF64748B),
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

class _ErrorCard extends StatelessWidget {
  final String message;
  final VoidCallback onRetry;

  const _ErrorCard({
    required this.message,
    required this.onRetry,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(14),
      decoration: BoxDecoration(
        color: const Color(0xFFFEF2F2),
        borderRadius: BorderRadius.circular(14),
        border: Border.all(color: const Color(0xFFFECACA)),
      ),
      child: Row(
        children: [
          const Icon(Icons.error_outline_rounded, color: Color(0xFFB91C1C)),
          const SizedBox(width: 10),
          Expanded(
            child: Text(
              message,
              style: const TextStyle(
                color: Color(0xFF7F1D1D),
                fontSize: 12,
                fontWeight: FontWeight.w600,
              ),
            ),
          ),
          TextButton(onPressed: onRetry, child: const Text('Tekrar Dene')),
        ],
      ),
    );
  }
}

class _RiskRadarSkeleton extends StatelessWidget {
  const _RiskRadarSkeleton();

  @override
  Widget build(BuildContext context) {
    return SizedBox(
      height: 168,
      child: ListView.separated(
        scrollDirection: Axis.horizontal,
        itemCount: 3,
        separatorBuilder: (context, index) => const SizedBox(width: 12),
        itemBuilder: (context, index) => Container(
          width: 250,
          decoration: BoxDecoration(
            color: Colors.white,
            borderRadius: BorderRadius.circular(18),
            border: Border.all(color: const Color(0xFFE2E8F0)),
          ),
          padding: const EdgeInsets.all(14),
          child: const Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              _ShimmerBox(width: 150, height: 16, radius: 8),
              SizedBox(height: 12),
              _ShimmerBox(width: 92, height: 24, radius: 999),
              SizedBox(height: 10),
              _ShimmerBox(width: 120, height: 12, radius: 6),
              Spacer(),
              _ShimmerBox(width: 80, height: 12, radius: 6),
            ],
          ),
        ),
      ),
    );
  }
}

class _RecentOrderSkeleton extends StatelessWidget {
  const _RecentOrderSkeleton();

  @override
  Widget build(BuildContext context) {
    return Column(
      children: List.generate(
        3,
        (_) => Container(
          margin: const EdgeInsets.only(bottom: 10),
          width: double.infinity,
          padding: const EdgeInsets.all(14),
          decoration: BoxDecoration(
            color: Colors.white,
            borderRadius: BorderRadius.circular(16),
            border: Border.all(color: const Color(0xFFE2E8F0)),
          ),
          child: const Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              _ShimmerBox(width: 160, height: 16, radius: 8),
              SizedBox(height: 8),
              _ShimmerBox(width: 120, height: 12, radius: 6),
              SizedBox(height: 8),
              _ShimmerBox(width: 90, height: 14, radius: 7),
              SizedBox(height: 12),
              Row(
                children: [
                  Expanded(child: _ShimmerBox(width: 100, height: 34, radius: 10)),
                  SizedBox(width: 8),
                  Expanded(child: _ShimmerBox(width: 100, height: 34, radius: 10)),
                ],
              ),
            ],
          ),
        ),
      ),
    );
  }
}

class _ShimmerBox extends StatefulWidget {
  final double width;
  final double height;
  final double radius;

  const _ShimmerBox({
    required this.width,
    required this.height,
    this.radius = 8,
  });

  @override
  State<_ShimmerBox> createState() => _ShimmerBoxState();
}

class _ShimmerBoxState extends State<_ShimmerBox>
    with SingleTickerProviderStateMixin {
  late final AnimationController _controller;

  @override
  void initState() {
    super.initState();
    _controller = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 1300),
    )..repeat();
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return AnimatedBuilder(
      animation: _controller,
      builder: (context, child) {
        final beginX = -1.0 + (2.0 * _controller.value);
        final endX = beginX + 2.0;
        return ShaderMask(
          shaderCallback: (bounds) {
            return LinearGradient(
              begin: Alignment(beginX, 0),
              end: Alignment(endX, 0),
              colors: const [
                Color(0xFFE2E8F0),
                Color(0xFFF8FAFC),
                Color(0xFFE2E8F0),
              ],
              stops: const [0.1, 0.45, 0.9],
            ).createShader(bounds);
          },
          blendMode: BlendMode.srcATop,
          child: child,
        );
      },
      child: Container(
        width: widget.width,
        height: widget.height,
        decoration: BoxDecoration(
          color: const Color(0xFFE2E8F0),
          borderRadius: BorderRadius.circular(widget.radius),
        ),
      ),
    );
  }
}
