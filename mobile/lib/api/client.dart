import 'dart:convert';
import 'package:http/http.dart' as http;
import 'models.dart';

// Linux desktop: localhost. Android emulator: 10.0.2.2. Physical device: LAN IP.
const String _baseUrl = 'http://localhost:9000';

Future<Patient> fetchPatient(int id) async {
  final res = await http.get(Uri.parse('$_baseUrl/patients/$id'));
  if (res.statusCode == 404) throw Exception('Patient introuvable');
  if (res.statusCode != 200) throw Exception('Erreur serveur');
  return Patient.fromJson(jsonDecode(res.body) as Map<String, dynamic>);
}

Future<List<Prescription>> fetchPrescriptions(int patientId) async {
  final res = await http.get(Uri.parse('$_baseUrl/patients/$patientId/prescriptions'));
  if (res.statusCode != 200) throw Exception('Erreur serveur');
  final List<dynamic> data = jsonDecode(res.body) as List<dynamic>;
  return data.map((e) => Prescription.fromJson(e as Map<String, dynamic>)).toList();
}

Future<List<Consultation>> fetchConsultations(int patientId) async {
  final res = await http.get(Uri.parse('$_baseUrl/patients/$patientId/consultations'));
  if (res.statusCode != 200) throw Exception('Erreur serveur');
  final List<dynamic> data = jsonDecode(res.body) as List<dynamic>;
  return data.map((e) => Consultation.fromJson(e as Map<String, dynamic>)).toList();
}
