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

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Consultations')),
      body: FutureBuilder<List<Consultation>>(
        future: _future,
        builder: (context, snapshot) {
          if (snapshot.connectionState == ConnectionState.waiting) {
            return const Center(child: CircularProgressIndicator());
          }
          if (snapshot.hasError) {
            return Center(child: Text('Erreur : ${snapshot.error}'));
          }
          final list = snapshot.data!;
          if (list.isEmpty) {
            return const Center(child: Text('Aucune consultation enregistrée.'));
          }
          return ListView.separated(
            padding: const EdgeInsets.all(16),
            itemCount: list.length,
            separatorBuilder: (_, _) => const SizedBox(height: 8),
            itemBuilder: (_, i) {
              final c = list[i];
              final date = DateTime.parse(c.date);
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
                            '${date.day}/${date.month}/${date.year}',
                            style: const TextStyle(fontWeight: FontWeight.bold),
                          ),
                          Text('Dr. ${c.doctorName}', style: const TextStyle(color: Colors.blueGrey, fontSize: 12)),
                        ],
                      ),
                      if (c.diagnosis != null) ...[
                        const SizedBox(height: 4),
                        Text(c.diagnosis!, style: const TextStyle(color: Colors.blue)),
                      ],
                      if (c.notes != null) ...[
                        const SizedBox(height: 4),
                        Text(c.notes!, style: const TextStyle(color: Colors.grey, fontSize: 13)),
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
