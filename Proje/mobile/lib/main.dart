import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:intl/date_symbol_data_local.dart';
import 'core/bloc/app_bloc_observer.dart';
import 'core/api/dio_client.dart';
import 'core/api/services/auth_api_service.dart';
import 'core/router/app_router.dart';
import 'features/auth/bloc/auth_bloc.dart';

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

    final router = AppRouter.create(authBloc);

    return MultiBlocProvider(
      providers: [
        BlocProvider.value(value: authBloc),
      ],
      child: MaterialApp.router(
        routerConfig: router,
        title: 'Gıda Nöbeti',
        debugShowCheckedModeBanner: false,
        theme: ThemeData(
          colorScheme: ColorScheme.fromSeed(seedColor: Colors.orange),
          useMaterial3: true,
        ),
      ),
    );
  }
}


