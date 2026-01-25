import 'package:equatable/equatable.dart';

/// Base state class for all BLoCs
/// Uses Equatable for efficient state comparison
abstract class BaseBlocState extends Equatable {
  const BaseBlocState();

  @override
  List<Object?> get props => [];
}
