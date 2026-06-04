import 'package:flutter/material.dart';
import '../api/client.dart';
import '../api/models.dart';

class ConsultationsScreen extends StatefulWidget {
  final int patientId;
  const ConsultationsScreen({super.key, required this.patientId});

  @override
  State<ConsultationsScreen> createState() => _ConsultationsScreenState();
}

class _ConsultationsScreenState extends State<ConsultationsScreen> {
  late Future<List<Consultation>> _future;

  @override
  void initState() {
    super.initState();
    _future = fetchConsultations(widget.patientId);
  }

  String _formatDate(String iso) {
    final d = DateTime.parse(iso);
    const months = ['jan', 'fév', 'mar', 'avr', 'mai', 'juin', 'juil', 'aoû', 'sep', 'oct', 'nov', 'déc'];
    return '${d.day} ${months[d.month - 1]}. ${d.year}';
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Mes consultations')),
      body: FutureBuilder<List<Consultation>>(
        future: _future,
        builder: (context, snapshot) {
          if (snapshot.connectionState == ConnectionState.waiting) {
            return const Center(child: CircularProgressIndicator(color: Color(0xFF0D9488)));
          }
          if (snapshot.hasError) {
            return Center(
              child: Padding(
                padding: const EdgeInsets.all(24),
                child: Text('Erreur : ${snapshot.error}', style: const TextStyle(color: Color(0xFFDC2626))),
              ),
            );
          }
          final list = snapshot.data!;
          if (list.isEmpty) {
            return const Center(
              child: Column(
                mainAxisSize: MainAxisSize.min,
                children: [
                  Text('📋', style: TextStyle(fontSize: 48)),
                  SizedBox(height: 12),
                  Text('Aucune consultation', style: TextStyle(fontSize: 16, fontWeight: FontWeight.w600, color: Color(0xFF1E293B))),
                  SizedBox(height: 4),
                  Text('Aucune consultation enregistrée.', style: TextStyle(color: Color(0xFF64748B))),
                ],
              ),
            );
          }
          return ListView.separated(
            padding: const EdgeInsets.all(16),
            itemCount: list.length,
            separatorBuilder: (_, _) => const SizedBox(height: 10),
            itemBuilder: (_, i) {
              final c = list[i];
              return Card(
                child: Padding(
                  padding: const EdgeInsets.all(16),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Row(
                        mainAxisAlignment: MainAxisAlignment.spaceBetween,
                        children: [
                          Text(
                            _formatDate(c.date),
                            style: const TextStyle(fontWeight: FontWeight.w600, fontSize: 14, color: Color(0xFF1E293B)),
                          ),
                          Text(
                            'Dr. ${c.doctorName}',
                            style: const TextStyle(fontSize: 12, color: Color(0xFF64748B)),
                          ),
                        ],
                      ),
                      if (c.diagnosis != null) ...[
                        const SizedBox(height: 8),
                        Container(
                          padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                          decoration: BoxDecoration(
                            color: const Color(0xFFCCFBF1),
                            borderRadius: BorderRadius.circular(6),
                          ),
                          child: Text(
                            c.diagnosis!,
                            style: const TextStyle(fontSize: 13, fontWeight: FontWeight.w600, color: Color(0xFF0F766E)),
                          ),
                        ),
                      ],
                      if (c.notes != null) ...[
                        const SizedBox(height: 8),
                        Text(c.notes!, style: const TextStyle(fontSize: 13, color: Color(0xFF64748B))),
                      ],
                    ],
                  ),
                ),
              );
            },
          );
        },
      ),
    );
  }
}
