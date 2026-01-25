import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:logger/logger.dart';

/// Global BLoC observer for debugging
/// Logs all state transitions and errors
class AppBlocObserver extends BlocObserver {
  final Logger _logger = Logger(
    printer: PrettyPrinter(
      methodCount: 0,
      errorMethodCount: 5,
      lineLength: 50,
      colors: true,
      printEmojis: true,
    ),
  );

  @override
  void onCreate(BlocBase bloc) {
    super.onCreate(bloc);
    _logger.d('🎉 onCreate: ${bloc.runtimeType}');
  }

  @override
  void onEvent(Bloc bloc, Object? event) {
    super.onEvent(bloc, event);
    _logger.i('📨 Event: ${bloc.runtimeType} | $event');
  }

  @override
  void onTransition(Bloc bloc, Transition transition) {
    super.onTransition(bloc, transition);
    _logger.i(
      '🔄 Transition: ${bloc.runtimeType}\n'
      '   Event: ${transition.event}\n'
      '   Current: ${transition.currentState}\n'
      '   Next: ${transition.nextState}',
    );
  }

  @override
  void onError(BlocBase bloc, Object error, StackTrace stackTrace) {
    super.onError(bloc, error, stackTrace);
    _logger.e(
      '❌ Error: ${bloc.runtimeType}',
      error: error,
      stackTrace: stackTrace,
    );
  }

  @override
  void onClose(BlocBase bloc) {
    super.onClose(bloc);
    _logger.d('👋 onClose: ${bloc.runtimeType}');
  }
}
