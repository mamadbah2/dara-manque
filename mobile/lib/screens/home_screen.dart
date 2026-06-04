import 'package:flutter/material.dart';
import '../api/models.dart';
import 'prescriptions_screen.dart';
import 'consultations_screen.dart';

class HomeScreen extends StatelessWidget {
  final Patient patient;
  const HomeScreen({super.key, required this.patient});

  String get _initials {
    final parts = patient.fullName.trim().split(' ');
    if (parts.length >= 2) return '${parts[0][0]}${parts[1][0]}'.toUpperCase();
    return parts[0][0].toUpperCase();
  }

  int? get _age {
    if (patient.dateOfBirth == null) return null;
    final dob = DateTime.tryParse(patient.dateOfBirth!);
    if (dob == null) return null;
    final now = DateTime.now();
    int age = now.year - dob.year;
    if (now.month < dob.month || (now.month == dob.month && now.day < dob.day)) age--;
    return age;
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Mon carnet de santé'),
        leading: IconButton(
          icon: const Icon(Icons.arrow_back),
          onPressed: () => Navigator.of(context).pop(),
        ),
      ),
      body: Padding(
        padding: const EdgeInsets.all(20),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            // Carte patient
            Card(
              child: Padding(
                padding: const EdgeInsets.all(20),
                child: Row(
                  children: [
                    CircleAvatar(
                      radius: 28,
                      backgroundColor: const Color(0xFF0D9488),
                      child: Text(
                        _initials,
                        style: const TextStyle(color: Colors.white, fontSize: 18, fontWeight: FontWeight.bold),
                      ),
                    ),
                    const SizedBox(width: 16),
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(
                            patient.fullName,
                            style: const TextStyle(fontSize: 18, fontWeight: FontWeight.bold, color: Color(0xFF1E293B)),
                          ),
                          const SizedBox(height: 8),
                          Wrap(
                            spacing: 6,
                            runSpacing: 6,
                            children: [
                              if (_age != null) _chip('$_age ans'),
                              if (patient.allergies != null)
                                _chip('⚠ ${patient.allergies!}', color: const Color(0xFFFEF2F2), textColor: const Color(0xFFDC2626)),
                              if (patient.chronicConditions != null)
                                _chip(patient.chronicConditions!),
                            ],
                          ),
                        ],
                      ),
                    ),
                  ],
                ),
              ),
            ),

            const SizedBox(height: 24),
            const Text(
              'ACCÈS RAPIDE',
              style: TextStyle(fontSize: 11, fontWeight: FontWeight.w600, color: Color(0xFF64748B), letterSpacing: 1.2),
            ),
            const SizedBox(height: 12),

            // Tuile Ordonnances
            _NavTile(
              icon: Icons.local_pharmacy_outlined,
              title: 'Mes ordonnances',
              subtitle: 'Ordonnances actives en cours',
              onTap: () => Navigator.of(context).push(
                MaterialPageRoute(builder: (_) => PrescriptionsScreen(patientId: patient.id)),
              ),
            ),
            const SizedBox(height: 12),

            // Tuile Consultations
            _NavTile(
              icon: Icons.medical_services_outlined,
              title: 'Mes consultations',
              subtitle: 'Historique des consultations',
              onTap: () => Navigator.of(context).push(
                MaterialPageRoute(builder: (_) => ConsultationsScreen(patientId: patient.id)),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _chip(String label, {Color? color, Color? textColor}) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
      decoration: BoxDecoration(
        color: color ?? const Color(0xFFCCFBF1),
        borderRadius: BorderRadius.circular(999),
      ),
      child: Text(
        label,
        style: TextStyle(fontSize: 12, fontWeight: FontWeight.w600, color: textColor ?? const Color(0xFF0F766E)),
      ),
    );
  }
}

class _NavTile extends StatelessWidget {
  final IconData icon;
  final String title;
  final String subtitle;
  final VoidCallback onTap;

  const _NavTile({required this.icon, required this.title, required this.subtitle, required this.onTap});

  @override
  Widget build(BuildContext context) {
    return Card(
      child: InkWell(
        onTap: onTap,
        borderRadius: BorderRadius.circular(12),
        child: Padding(
          padding: const EdgeInsets.all(18),
          child: Row(
            children: [
              Container(
                width: 44, height: 44,
                decoration: BoxDecoration(
                  color: const Color(0xFFCCFBF1),
                  borderRadius: BorderRadius.circular(10),
                ),
                child: Icon(icon, color: const Color(0xFF0D9488), size: 22),
              ),
              const SizedBox(width: 16),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(title, style: const TextStyle(fontWeight: FontWeight.w600, fontSize: 15, color: Color(0xFF1E293B))),
                    const SizedBox(height: 2),
                    Text(subtitle, style: const TextStyle(fontSize: 13, color: Color(0xFF64748B))),
                  ],
                ),
              ),
              const Icon(Icons.chevron_right, color: Color(0xFF94A3B8)),
            ],
          ),
        ),
      ),
    );
  }
}
