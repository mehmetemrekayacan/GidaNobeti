import 'dart:async';

import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';

import 'app_routes.dart';
import '../../features/auth/bloc/auth_bloc.dart';
import '../../features/auth/screens/login_screen.dart';
import '../../features/auth/screens/register_screen.dart';
import '../../features/home/screens/home_screen.dart';
import '../../features/incident/screens/incident_report_screen.dart';
import '../../features/incident/screens/my_incidents_screen.dart';
import '../../features/order/screens/order_history_screen.dart';
import '../../features/order/screens/order_upload_screen.dart';
import '../../features/profile/screens/profile_screen.dart';
import '../../features/restaurant/screens/restaurant_detail_screen.dart';
import '../../features/restaurant/screens/restaurant_list_screen.dart';
import '../../features/restaurant/screens/risky_restaurants_screen.dart';

class AppRouter {
  AppRouter._();

  static GoRouter create(AuthBloc authBloc) {
    return GoRouter(
      initialLocation: AppRoutes.homePath,
      refreshListenable: GoRouterAuthRefresh(authBloc.stream),
      redirect: (context, state) {
        final AuthState authState = authBloc.state;
        final String location = state.uri.path;

        final bool isLoadingState =
            authState is AuthInitial || authState is AuthLoading;
        final bool isAuthenticated = authState is AuthAuthenticated;
        final bool isAuthRoute = location == AppRoutes.loginPath ||
            location == AppRoutes.registerPath;
        final bool isSplashRoute = location == AppRoutes.splashPath;

        if (location == '/') {
          return AppRoutes.homePath;
        }

        if (isLoadingState) {
          return isSplashRoute ? null : AppRoutes.splashPath;
        }

        if (!isAuthenticated && !isAuthRoute) {
          return AppRoutes.loginPath;
        }

        if (isAuthenticated && isAuthRoute) {
          return AppRoutes.homePath;
        }

        if (isSplashRoute) {
          return isAuthenticated ? AppRoutes.homePath : AppRoutes.loginPath;
        }

        return null;
      },
      routes: <GoRoute>[
        GoRoute(
          name: AppRoutes.splashName,
          path: AppRoutes.splashPath,
          builder: (context, state) => const _SplashScreen(),
        ),
        GoRoute(
          name: AppRoutes.loginName,
          path: AppRoutes.loginPath,
          builder: (context, state) => const LoginScreen(),
        ),
        GoRoute(
          name: AppRoutes.registerName,
          path: AppRoutes.registerPath,
          builder: (context, state) => const RegisterScreen(),
        ),
        GoRoute(
          name: AppRoutes.homeName,
          path: AppRoutes.homePath,
          builder: (context, state) => const HomeScreen(),
        ),
        GoRoute(
          name: AppRoutes.orderUploadName,
          path: AppRoutes.orderUploadPath,
          builder: (context, state) => const OrderUploadScreen(),
        ),
        GoRoute(
          name: AppRoutes.orderHistoryName,
          path: AppRoutes.orderHistoryPath,
          builder: (context, state) => const OrderHistoryScreen(),
        ),
        GoRoute(
          name: AppRoutes.incidentReportName,
          path: AppRoutes.incidentReportPath,
          builder: (context, state) => const IncidentReportScreen(),
        ),
        GoRoute(
          name: AppRoutes.myIncidentsName,
          path: AppRoutes.myIncidentsPath,
          builder: (context, state) => const MyIncidentsScreen(),
        ),
        GoRoute(
          name: AppRoutes.restaurantListName,
          path: AppRoutes.restaurantListPath,
          builder: (context, state) => const RestaurantListScreen(),
        ),
        GoRoute(
          name: AppRoutes.riskyRestaurantsName,
          path: AppRoutes.riskyRestaurantsPath,
          builder: (context, state) => const RiskyRestaurantsScreen(),
        ),
        GoRoute(
          name: AppRoutes.restaurantDetailName,
          path: AppRoutes.restaurantDetailPathPattern,
          builder: (context, state) {
            final String? idValue = state.pathParameters['id'];
            final int? restaurantId = int.tryParse(idValue ?? '');

            if (restaurantId == null) {
              return const _RouteErrorScreen(
                message: 'Geçersiz restoran kimliği',
              );
            }

            return RestaurantDetailScreen(restaurantId: restaurantId);
          },
        ),
        GoRoute(
          name: AppRoutes.profileName,
          path: AppRoutes.profilePath,
          builder: (context, state) => const ProfileScreen(),
        ),
      ],
      errorBuilder: (context, state) =>
          _RouteErrorScreen(message: state.error.toString()),
    );
  }
}

class GoRouterAuthRefresh extends ChangeNotifier {
  GoRouterAuthRefresh(Stream<AuthState> stream) {
    _subscription = stream.asBroadcastStream().listen((_) {
      notifyListeners();
    });
  }

  late final StreamSubscription<AuthState> _subscription;

  @override
  void dispose() {
    _subscription.cancel();
    super.dispose();
  }
}

class _SplashScreen extends StatelessWidget {
  const _SplashScreen();

  @override
  Widget build(BuildContext context) {
    return const Scaffold(
      body: Center(
        child: CircularProgressIndicator(),
      ),
    );
  }
}

class _RouteErrorScreen extends StatelessWidget {
  final String message;

  const _RouteErrorScreen({required this.message});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Yönlendirme Hatası')),
      body: Center(
        child: Padding(
          padding: const EdgeInsets.all(24.0),
          child: Text(
            message,
            textAlign: TextAlign.center,
          ),
        ),
      ),
    );
  }
}
