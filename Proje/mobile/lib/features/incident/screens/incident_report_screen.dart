import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:go_router/go_router.dart';
import 'package:intl/intl.dart';

import '../../../core/api/models/order_models.dart';
import '../../../core/router/app_routes.dart';
import '../bloc/incident_bloc.dart';

class IncidentReportScreen extends StatelessWidget {
  const IncidentReportScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return BlocProvider(
      create: (_) => IncidentBloc()..add(const IncidentOrdersRequested()),
      child: const _IncidentReportView(),
    );
  }
}

class _IncidentReportView extends StatefulWidget {
  const _IncidentReportView();

  @override
  State<_IncidentReportView> createState() => _IncidentReportViewState();
}

class _IncidentReportViewState extends State<_IncidentReportView> {
  final _formKey = GlobalKey<FormState>();
  final _symptomsController = TextEditingController();

  String? _selectedOrderId;
  String? _selectedSeverity = 'Orta';
  bool _isDoctorVerified = false;

  static const Map<String, int> _severityToValue = {
    'Hafif': 1,
    'Orta': 3,
    'Ağır': 5,
  };

  @override
  void dispose() {
    _symptomsController.dispose();
    super.dispose();
  }

  void _showSuccessDialog(String incidentId, List<String> nextSteps) {
    showDialog(
      context: context,
      barrierDismissible: true,
      builder: (ctx) => AlertDialog(
        title: const Row(
          children: [
            Icon(Icons.check_circle, color: Colors.green, size: 28),
            SizedBox(width: 8),
            Text('Bildirim alındı'),
          ],
        ),
        content: SingleChildScrollView(
          child: Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                'Kayıt no: $incidentId',
                style: TextStyle(
                  fontSize: 12,
                  color: Colors.grey[600],
                ),
              ),
              if (nextSteps.isNotEmpty) ...[
                const SizedBox(height: 12),
                const Text(
                  'Önerilen adımlar:',
                  style: TextStyle(
                    fontWeight: FontWeight.w600,
                    fontSize: 14,
                  ),
                ),
                const SizedBox(height: 6),
                ...nextSteps.map(
                  (s) => Padding(
                    padding: const EdgeInsets.only(bottom: 4),
                    child: Row(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text('• ', style: TextStyle(color: Colors.grey[700])),
                        Expanded(child: Text(s)),
                      ],
                    ),
                  ),
                ),
              ],
              const SizedBox(height: 12),
              Text(
                'Lütfen sağlık görevlisine de başvurunuz.',
                style: TextStyle(
                  fontWeight: FontWeight.w500,
                  color: Colors.orange[800],
                  fontSize: 13,
                ),
              ),
            ],
          ),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(ctx).pop(),
            child: const Text('Tamam'),
          ),
        ],
      ),
    ).then((_) {
      if (!mounted) return;
      context.read<IncidentBloc>().add(const IncidentReportStatusResetRequested());
      setState(() {
        _symptomsController.clear();
      });
    });
  }

  void _submit(List<OrderHistoryEntry> orders) {
    final isValid = _formKey.currentState?.validate() ?? false;
    if (!isValid) return;

    OrderHistoryEntry? order;
    for (final o in orders) {
      if (o.id == _selectedOrderId) {
        order = o;
        break;
      }
    }

    final severityLabel = _selectedSeverity;
    final severityLevel =
        severityLabel == null ? null : _severityToValue[severityLabel];

    if (order == null || severityLevel == null) {
      return;
    }

    context.read<IncidentBloc>().add(
          IncidentReportSubmitted(
            suspectedOrderId: order.id,
            symptoms: _symptomsController.text.trim(),
            severityLevel: severityLevel,
            isVerifiedByDoctor: _isDoctorVerified,
          ),
        );
  }

  @override
  Widget build(BuildContext context) {
    return BlocConsumer<IncidentBloc, IncidentState>(
      listenWhen: (previous, current) =>
          previous.submitStatus != current.submitStatus ||
          previous.ordersStatus != current.ordersStatus,
      listener: (context, state) {
        if (_selectedOrderId == null && state.orders.isNotEmpty) {
          setState(() {
            _selectedOrderId = state.orders.first.id;
          });
        }

        if (state.submitStatus == IncidentRequestStatus.success &&
            state.submitResponse != null) {
          WidgetsBinding.instance.addPostFrameCallback((_) {
            if (!mounted) return;
            _showSuccessDialog(
              state.submitResponse!.incidentId,
              state.submitResponse!.nextSteps,
            );
          });
        }
      },
      builder: (context, state) {
        final isOrdersLoading = state.ordersStatus == IncidentRequestStatus.loading;
        final isSubmitting = state.submitStatus == IncidentRequestStatus.loading;

        return Scaffold(
          appBar: AppBar(
            title: const Text('Sağlık Sorunu Bildir'),
            actions: [
              TextButton.icon(
                onPressed: () => context.pushNamed(AppRoutes.myIncidentsName),
                icon: const Icon(Icons.list_alt, size: 20, color: Colors.white),
                label: const Text(
                  'Bildirimlerim',
                  style: TextStyle(color: Colors.white),
                ),
              ),
            ],
          ),
          body: SingleChildScrollView(
            padding: const EdgeInsets.all(20),
            child: Form(
              key: _formKey,
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.stretch,
                children: [
                  Card(
                    color: Theme.of(context).colorScheme.primaryContainer,
                    child: const Padding(
                      padding: EdgeInsets.all(16),
                      child: Row(
                        children: [
                          Icon(Icons.info_outline),
                          SizedBox(width: 12),
                          Expanded(
                            child: Text(
                              'Bir siparişten sonra rahatsızlandıysanız bildirim yapabilirsiniz. Sağlık görevlisine de başvurunuz.',
                              style: TextStyle(fontSize: 13),
                            ),
                          ),
                        ],
                      ),
                    ),
                  ),
                  const SizedBox(height: 20),
                  const Text(
                    'Hangi siparişten şüpheleniliyor?',
                    style: TextStyle(
                      fontWeight: FontWeight.w600,
                      fontSize: 14,
                    ),
                  ),
                  const SizedBox(height: 8),
                  if (isOrdersLoading)
                    const Row(
                      children: [
                        SizedBox(
                          width: 18,
                          height: 18,
                          child: CircularProgressIndicator(strokeWidth: 2),
                        ),
                        SizedBox(width: 10),
                        Text('Siparişler yükleniyor...'),
                      ],
                    )
                  else if (state.ordersStatus == IncidentRequestStatus.failure &&
                      state.ordersError != null)
                    Text(state.ordersError!, style: TextStyle(color: Colors.red[700]))
                  else ...[
                    DropdownButtonFormField<String>(
                      value: state.orders.isEmpty ? null : _selectedOrderId,
                      decoration: const InputDecoration(
                        border: OutlineInputBorder(),
                        contentPadding:
                            EdgeInsets.symmetric(horizontal: 12, vertical: 12),
                      ),
                      items: state.orders.map((o) {
                        final restaurantName = o.restaurant?.name ?? 'Restoran';
                        final orderDate = DateFormat('dd.MM.yyyy').format(o.declaredAt);
                        return DropdownMenuItem<String>(
                          value: o.id,
                          child: Text(
                            '$restaurantName - $orderDate',
                            overflow: TextOverflow.ellipsis,
                            maxLines: 1,
                          ),
                        );
                      }).toList(),
                      onChanged: state.orders.isEmpty
                          ? null
                          : (v) {
                              setState(() {
                                _selectedOrderId = v;
                              });
                            },
                      validator: (value) {
                        if (state.orders.isEmpty) {
                          return null;
                        }
                        if (value == null || value.isEmpty) {
                          return 'Lütfen şüphelenilen siparişi seçin.';
                        }
                        return null;
                      },
                    ),
                    if (state.orders.isEmpty) ...[
                      const SizedBox(height: 8),
                      Text(
                        'Bildirim yapabilmek için en az bir geçmiş siparişiniz bulunmalıdır.',
                        style: TextStyle(
                          color: Theme.of(context).colorScheme.error,
                          fontSize: 13,
                        ),
                      ),
                    ],
                  ],
                  const SizedBox(height: 20),
                  const Text(
                    'Belirtiler (Semptomlar)',
                    style: TextStyle(
                      fontWeight: FontWeight.w600,
                      fontSize: 14,
                    ),
                  ),
                  const SizedBox(height: 8),
                  TextFormField(
                    controller: _symptomsController,
                    keyboardType: TextInputType.multiline,
                    textInputAction: TextInputAction.newline,
                    maxLines: 4,
                    maxLength: 2000,
                    decoration: const InputDecoration(
                      hintText: 'Örn: Mide bulantısı, baş ağrısı, kusma...',
                      border: OutlineInputBorder(),
                      alignLabelWithHint: true,
                    ),
                    validator: (value) {
                      final symptoms = (value ?? '').trim();
                      if (symptoms.isEmpty) {
                        return 'Belirti alanı boş bırakılamaz.';
                      }
                      if (symptoms.length < 10) {
                        return 'Semptomları en az 10 karakter olacak şekilde yazın.';
                      }
                      if (symptoms.length > 2000) {
                        return 'Semptomlar en fazla 2000 karakter olabilir.';
                      }
                      return null;
                    },
                  ),
                  const SizedBox(height: 20),
                  const Text(
                    'Şiddet Seviyesi',
                    style: TextStyle(
                      fontWeight: FontWeight.w600,
                      fontSize: 14,
                    ),
                  ),
                  const SizedBox(height: 8),
                  DropdownButtonFormField<String>(
                    value: _selectedSeverity,
                    decoration: const InputDecoration(
                      border: OutlineInputBorder(),
                    ),
                    items: _severityToValue.keys
                        .map(
                          (level) => DropdownMenuItem<String>(
                            value: level,
                            child: Text(level),
                          ),
                        )
                        .toList(),
                    onChanged: (value) {
                      setState(() {
                        _selectedSeverity = value;
                      });
                    },
                    validator: (value) {
                      if (value == null || value.isEmpty) {
                        return 'Lütfen şiddet seviyesi seçin.';
                      }
                      return null;
                    },
                  ),
                  const SizedBox(height: 16),
                  SwitchListTile.adaptive(
                    contentPadding: const EdgeInsets.symmetric(horizontal: 4),
                    title: const Text('Hastaneye gidildi / Doktor onaylı'),
                    subtitle: const Text('Doktor tarafından doğrulandıysa işaretleyin'),
                    value: _isDoctorVerified,
                    onChanged: isSubmitting
                        ? null
                        : (value) => setState(() => _isDoctorVerified = value),
                  ),
                  const SizedBox(height: 24),
                  if (state.submitStatus == IncidentRequestStatus.failure &&
                      state.submitError != null) ...[
                    Text(
                      state.submitError!,
                      style: TextStyle(color: Colors.red[700], fontSize: 13),
                    ),
                    const SizedBox(height: 12),
                  ],
                  ElevatedButton(
                    onPressed: isSubmitting ? null : () => _submit(state.orders),
                    style: ElevatedButton.styleFrom(
                      padding: const EdgeInsets.symmetric(vertical: 16),
                    ),
                    child: isSubmitting
                        ? const SizedBox(
                            height: 24,
                            width: 24,
                            child: CircularProgressIndicator(
                              strokeWidth: 2,
                              color: Colors.white,
                            ),
                          )
                        : const Text('Bildir'),
                  ),
                ],
              ),
            ),
          ),
        );
      },
    );
  }
}
