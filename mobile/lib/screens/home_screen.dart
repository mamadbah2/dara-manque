import 'package:flutter/material.dart';
import '../api/models.dart';
import 'prescriptions_screen.dart';
import 'consultations_screen.dart';

class HomeScreen extends StatelessWidget {
  final Patient patient;
  const HomeScreen({super.key, required this.patient});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Mon dossier'),
        leading: IconButton(
          icon: const Icon(Icons.arrow_back),
          onPressed: () => Navigator.of(context).pop(),
        ),
      ),
      body: Padding(
        padding: const EdgeInsets.all(24),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(patient.fullName, style: const TextStyle(fontSize: 22, fontWeight: FontWeight.bold)),
            const SizedBox(height: 8),
            if (patient.allergies != null)
              Text('Allergies : ${patient.allergies}', style: const TextStyle(color: Colors.red)),
            if (patient.chronicConditions != null)
              Text('Maladies chroniques : ${patient.chronicConditions}'),
            const SizedBox(height: 32),
            ListTile(
              leading: const Icon(Icons.medication, color: Colors.blue),
              title: const Text('Ordonnances actives'),
              trailing: const Icon(Icons.chevron_right),
              tileColor: Colors.white,
              shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8)),
              onTap: () => Navigator.of(context).push(
                MaterialPageRoute(builder: (_) => PrescriptionsScreen(patientId: patient.id)),
              ),
            ),
            const SizedBox(height: 12),
            ListTile(
              leading: const Icon(Icons.history, color: Colors.green),
              title: const Text('Historique des consultations'),
              trailing: const Icon(Icons.chevron_right),
              tileColor: Colors.white,
              shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8)),
              onTap: () => Navigator.of(context).push(
                MaterialPageRoute(builder: (_) => ConsultationsScreen(patientId: patient.id)),
              ),
            ),
          ],
        ),
      ),
    );
  }
}
