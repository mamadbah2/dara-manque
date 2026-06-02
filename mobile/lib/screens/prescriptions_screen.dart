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

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Ordonnances actives')),
      body: FutureBuilder<List<Prescription>>(
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
            return const Center(child: Text('Aucune ordonnance active.'));
          }
          return ListView.separated(
            padding: const EdgeInsets.all(16),
            itemCount: list.length,
            separatorBuilder: (_, _) => const SizedBox(height: 8),
            itemBuilder: (_, i) {
              final p = list[i];
              final date = DateTime.parse(p.createdAt);
              return Card(
                child: Padding(
                  padding: const EdgeInsets.all(16),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        '${date.day}/${date.month}/${date.year}',
                        style: const TextStyle(color: Colors.grey, fontSize: 12),
                      ),
                      const SizedBox(height: 4),
                      Text(p.medications, style: const TextStyle(fontSize: 15)),
                      const SizedBox(height: 4),
                      Text('Dr. ${p.doctorName}', style: const TextStyle(color: Colors.blueGrey, fontSize: 13)),
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
