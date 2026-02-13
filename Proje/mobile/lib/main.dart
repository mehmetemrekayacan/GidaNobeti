import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:intl/date_symbol_data_local.dart';
import 'core/bloc/app_bloc_observer.dart';
import 'core/api/dio_client.dart';
import 'core/api/services/auth_api_service.dart';
import 'features/auth/bloc/auth_bloc.dart';
import 'features/auth/screens/login_screen.dart';
import 'features/auth/screens/register_screen.dart';
import 'features/home/screens/home_screen.dart';
import 'features/restaurant/screens/restaurant_list_screen.dart';
import 'features/restaurant/screens/restaurant_detail_screen.dart';
import 'features/restaurant/screens/risky_restaurants_screen.dart';
import 'features/order/screens/order_upload_screen.dart';
import 'features/order/screens/order_history_screen.dart';
import 'features/incident/screens/incident_report_screen.dart';
import 'features/incident/screens/my_incidents_screen.dart';

void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  await initializeDateFormatting('tr', null);

  // Setup BLoC observer for debugging
  Bloc.observer = AppBlocObserver();

  runApp(const MyApp());
}

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context) {
    // Initialize API services
    final dioClient = DioClient();
    final authApiService = AuthApiService(dioClient);

    // Setup 401 handler - logout on token expiration
    final authBloc = AuthBloc(authApiService)..add(const AuthCheckRequested());
    DioClient.onUnauthorized = () {
      authBloc.add(const AuthLogoutRequested());
    };

    return MultiBlocProvider(
      providers: [
        BlocProvider.value(value: authBloc),
      ],
      child: MaterialApp(
        title: 'Gıda Nöbeti',
        debugShowCheckedModeBanner: false,
        theme: ThemeData(
          colorScheme: ColorScheme.fromSeed(seedColor: Colors.orange),
          useMaterial3: true,
        ),
        initialRoute: '/',
        routes: {
          '/': (context) => const AuthGate(),
          '/login': (context) => const LoginScreen(),
          '/register': (context) => const RegisterScreen(),
          '/home': (context) => const HomeScreen(),
          '/restaurants': (context) => const RestaurantListScreen(),
          '/risky-restaurants': (context) => const RiskyRestaurantsScreen(),
          '/order-upload': (context) => const OrderUploadScreen(),
          '/order-history': (context) => const OrderHistoryScreen(),
          '/incident-report': (context) => const IncidentReportScreen(),
          '/my-incidents': (context) => const MyIncidentsScreen(),
        },
        onGenerateRoute: (settings) {
          if (settings.name == '/restaurant-detail') {
            final restaurantId = settings.arguments as int;
            return MaterialPageRoute(
              builder: (context) => RestaurantDetailScreen(restaurantId: restaurantId),
            );
          }
          return null;
        },
      ),
    );
  }
}

/// Auth Gate - Determines initial route based on auth state
class AuthGate extends StatelessWidget {
  const AuthGate({super.key});

  @override
  Widget build(BuildContext context) {
    return BlocBuilder<AuthBloc, AuthState>(
      builder: (context, state) {
        if (state is AuthAuthenticated) {
          return const HomeScreen();
        } else if (state is AuthUnauthenticated) {
          return const LoginScreen();
        } else {
          // Loading state
          return const Scaffold(
            body: Center(
              child: CircularProgressIndicator(),
            ),
          );
        }
      },
    );
  }
}

