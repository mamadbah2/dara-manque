import 'package:flutter/material.dart';
import '../api/client.dart';
import '../api/models.dart';

class PrescriptionsScreen extends StatefulWidget {
  final int patientId;
  const PrescriptionsScreen({super.key, required this.patientId});

  @override
  State<PrescriptionsScreen> createState() => _PrescriptionsScreenState();
}

class _PrescriptionsScreenState extends State<PrescriptionsScreen> {
  late Future<List<Prescription>> _future;

  @override
  void initState() {
    super.initState();
    _future = fetchPrescriptions(widget.patientId);
  }

  String _formatDate(String iso) {
    final d = DateTime.parse(iso);
    const months = ['jan', 'fév', 'mar', 'avr', 'mai', 'juin', 'juil', 'aoû', 'sep', 'oct', 'nov', 'déc'];
    return '${d.day} ${months[d.month - 1]}. ${d.year}';
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Mes ordonnances')),
      body: FutureBuilder<List<Prescription>>(
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
                  Text('🎉', style: TextStyle(fontSize: 48)),
                  SizedBox(height: 12),
                  Text('Aucune ordonnance active', style: TextStyle(fontSize: 16, fontWeight: FontWeight.w600, color: Color(0xFF1E293B))),
                  SizedBox(height: 4),
                  Text('Tout va bien pour l\'instant !', style: TextStyle(color: Color(0xFF64748B))),
                ],
              ),
            );
          }
          return ListView.separated(
            padding: const EdgeInsets.all(16),
            itemCount: list.length,
            separatorBuilder: (_, _) => const SizedBox(height: 10),
            itemBuilder: (_, i) {
              final p = list[i];
              return Card(
                child: Padding(
                  padding: const EdgeInsets.all(16),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Row(
                        children: [
                          Container(
                            padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                            decoration: BoxDecoration(
                              color: const Color(0xFFFFFBEB),
                              borderRadius: BorderRadius.circular(999),
                            ),
                            child: const Text(
                              '● Active',
                              style: TextStyle(fontSize: 12, fontWeight: FontWeight.w600, color: Color(0xFFD97706)),
                            ),
                          ),
                          const Spacer(),
                          Text(
                            _formatDate(p.createdAt),
                            style: const TextStyle(fontSize: 12, color: Color(0xFF64748B)),
                          ),
                        ],
                      ),
                      const SizedBox(height: 12),
                      Text(
                        p.medications,
                        style: const TextStyle(fontSize: 15, fontWeight: FontWeight.w600, color: Color(0xFF1E293B)),
                      ),
                      const SizedBox(height: 6),
                      Text(
                        'Dr. ${p.doctorName}',
                        style: const TextStyle(fontSize: 13, color: Color(0xFF64748B)),
                      ),
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
