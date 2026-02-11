import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
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

void main() {
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

    return MultiBlocProvider(
      providers: [
        BlocProvider(
          create: (context) => AuthBloc(authApiService)
            ..add(const AuthCheckRequested()),
        ),
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

