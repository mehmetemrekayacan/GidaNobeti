import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:intl/date_symbol_data_local.dart';
import 'package:intl/intl.dart';

import '../bloc/incident_bloc.dart';

class MyIncidentsScreen extends StatelessWidget {
  const MyIncidentsScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return BlocProvider(
      create: (_) => IncidentBloc(),
      child: const _MyIncidentsView(),
    );
  }
}

class _MyIncidentsView extends StatefulWidget {
  const _MyIncidentsView();

  @override
  State<_MyIncidentsView> createState() => _MyIncidentsViewState();
}

class _MyIncidentsViewState extends State<_MyIncidentsView> {
  @override
  void initState() {
    super.initState();
    _initializeLocale();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      _load();
    });
  }

  Future<void> _initializeLocale() async {
    await initializeDateFormatting('tr_TR', null);
  }

  Future<void> _load() async {
    context.read<IncidentBloc>().add(const IncidentListRequested(page: 1, limit: 50));
  }

  String _statusLabel(String status) {
    switch (status) {
      case 'PENDING':
        return 'Beklemede';
      case 'INVESTIGATING':
        return 'İnceleniyor';
      case 'CONFIRMED':
        return 'Onaylandı';
      case 'DISMISSED':
        return 'Reddedildi';
      default:
        return status;
    }
  }

  Color _statusColor(String status) {
    switch (status) {
      case 'CONFIRMED':
        return Colors.green;
      case 'DISMISSED':
        return Colors.grey;
      case 'INVESTIGATING':
        return Colors.orange;
      default:
        return Colors.blue;
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Bildirimlerim'),
        backgroundColor: Colors.orange,
        foregroundColor: Colors.white,
        actions: [
          BlocBuilder<IncidentBloc, IncidentState>(
            buildWhen: (previous, current) =>
                previous.incidentsStatus != current.incidentsStatus,
            builder: (context, state) {
              final isLoading =
                  state.incidentsStatus == IncidentRequestStatus.loading;
              return IconButton(
                icon: const Icon(Icons.refresh),
                onPressed: isLoading ? null : _load,
              );
            },
          ),
        ],
      ),
      body: BlocBuilder<IncidentBloc, IncidentState>(
        buildWhen: (previous, current) =>
            previous.incidentsStatus != current.incidentsStatus ||
            previous.incidents != current.incidents ||
            previous.incidentsError != current.incidentsError,
        builder: (context, state) {
          final isLoading = state.incidentsStatus == IncidentRequestStatus.loading;

          return RefreshIndicator(
            onRefresh: _load,
            child: isLoading
                ? const Center(child: CircularProgressIndicator())
                : state.incidentsStatus == IncidentRequestStatus.failure &&
                        state.incidentsError != null
                    ? Center(
                        child: Padding(
                          padding: const EdgeInsets.all(24),
                          child: Column(
                            mainAxisSize: MainAxisSize.min,
                            children: [
                              Icon(Icons.error_outline, size: 48, color: Colors.red[300]),
                              const SizedBox(height: 16),
                              Text(
                                state.incidentsError!,
                                textAlign: TextAlign.center,
                                style: TextStyle(color: Colors.red[700]),
                              ),
                              const SizedBox(height: 16),
                              ElevatedButton(
                                onPressed: _load,
                                child: const Text('Tekrar dene'),
                              ),
                            ],
                          ),
                        ),
                      )
                    : state.incidents.isEmpty
                        ? ListView(
                            physics: const AlwaysScrollableScrollPhysics(),
                            children: [
                              SizedBox(
                                height: MediaQuery.of(context).size.height * 0.4,
                                child: Center(
                                  child: Column(
                                    mainAxisSize: MainAxisSize.min,
                                    children: [
                                      Icon(
                                        Icons.medical_services_outlined,
                                        size: 64,
                                        color: Colors.grey[400],
                                      ),
                                      const SizedBox(height: 16),
                                      Text(
                                        'Henüz bildiriminiz yok',
                                        style: TextStyle(
                                          fontSize: 16,
                                          color: Colors.grey[600],
                                        ),
                                      ),
                                      const SizedBox(height: 8),
                                      Text(
                                        'Sağlık sorunu bildirimi yaptığınızda\nburada listelenecek.',
                                        textAlign: TextAlign.center,
                                        style: TextStyle(
                                          fontSize: 13,
                                          color: Colors.grey[500],
                                        ),
                                      ),
                                    ],
                                  ),
                                ),
                              ),
                            ],
                          )
                        : ListView.builder(
                            physics: const AlwaysScrollableScrollPhysics(),
                            padding: const EdgeInsets.symmetric(vertical: 12),
                            itemCount: state.incidents.length,
                            itemBuilder: (context, index) {
                              final item = state.incidents[index];
                              return Card(
                                margin: const EdgeInsets.symmetric(
                                  horizontal: 16,
                                  vertical: 6,
                                ),
                                child: ListTile(
                                  contentPadding: const EdgeInsets.symmetric(
                                    horizontal: 16,
                                    vertical: 12,
                                  ),
                                  leading: CircleAvatar(
                                    backgroundColor: _statusColor(item.status)
                                        .withOpacity(0.2),
                                    child: Icon(
                                      Icons.medical_information_outlined,
                                      color: _statusColor(item.status),
                                    ),
                                  ),
                                  title: Text(
                                    item.restaurantName ?? 'Restoran bilinmiyor',
                                    style: const TextStyle(
                                      fontWeight: FontWeight.w600,
                                      fontSize: 15,
                                    ),
                                  ),
                                  subtitle: Column(
                                    crossAxisAlignment: CrossAxisAlignment.start,
                                    children: [
                                      const SizedBox(height: 4),
                                      Text(
                                        item.symptoms,
                                        maxLines: 2,
                                        overflow: TextOverflow.ellipsis,
                                        style: TextStyle(
                                          fontSize: 13,
                                          color: Colors.grey[700],
                                        ),
                                      ),
                                      const SizedBox(height: 6),
                                      Row(
                                        children: [
                                          Container(
                                            padding: const EdgeInsets.symmetric(
                                              horizontal: 8,
                                              vertical: 2,
                                            ),
                                            decoration: BoxDecoration(
                                              color: _statusColor(item.status)
                                                  .withOpacity(0.15),
                                              borderRadius: BorderRadius.circular(6),
                                            ),
                                            child: Text(
                                              _statusLabel(item.status),
                                              style: TextStyle(
                                                fontSize: 12,
                                                fontWeight: FontWeight.w500,
                                                color: _statusColor(item.status),
                                              ),
                                            ),
                                          ),
                                          if (item.severityLevel != null) ...[
                                            const SizedBox(width: 8),
                                            Text(
                                              'Şiddet ${item.severityLevel}/5',
                                              style: TextStyle(
                                                fontSize: 12,
                                                color: Colors.grey[600],
                                              ),
                                            ),
                                          ],
                                        ],
                                      ),
                                      const SizedBox(height: 4),
                                      Text(
                                        DateFormat('d.M.y HH:mm', 'tr_TR').format(item.reportDate),
                                        style: TextStyle(
                                          fontSize: 11,
                                          color: Colors.grey[500],
                                        ),
                                      ),
                                    ],
                                  ),
                                  isThreeLine: true,
                                ),
                              );
                            },
                          ),
          );
        },
      ),
    );
  }
}
