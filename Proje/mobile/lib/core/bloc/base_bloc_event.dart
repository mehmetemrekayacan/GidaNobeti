import 'package:equatable/equatable.dart';

/// Base event class for all BLoCs
/// Uses Equatable for efficient event comparison
abstract class BaseBlocEvent extends Equatable {
  const BaseBlocEvent();

  @override
  List<Object?> get props => [];
}
