class Patient {
  final int id;
  final String fullName;
  final String? dateOfBirth;
  final String? allergies;
  final String? chronicConditions;
  final String? cardUid;

  const Patient({
    required this.id,
    required this.fullName,
    this.dateOfBirth,
    this.allergies,
    this.chronicConditions,
    this.cardUid,
  });

  factory Patient.fromJson(Map<String, dynamic> json) => Patient(
        id: json['id'] as int,
        fullName: json['full_name'] as String,
        dateOfBirth: json['date_of_birth'] as String?,
        allergies: json['allergies'] as String?,
        chronicConditions: json['chronic_conditions'] as String?,
        cardUid: json['card_uid'] as String?,
      );
}

class Prescription {
  final String id;
  final String createdAt;
  final String medications;
  final String status;
  final String doctorName;

  const Prescription({
    required this.id,
    required this.createdAt,
    required this.medications,
    required this.status,
    required this.doctorName,
  });

  factory Prescription.fromJson(Map<String, dynamic> json) => Prescription(
        id: json['id'] as String,
        createdAt: json['created_at'] as String,
        medications: json['medications'] as String,
        status: json['status'] as String,
        doctorName: json['doctor_name'] as String,
      );
}

class Consultation {
  final String id;
  final String date;
  final String? notes;
  final String? diagnosis;
  final String doctorName;

  const Consultation({
    required this.id,
    required this.date,
    this.notes,
    this.diagnosis,
    required this.doctorName,
  });

  factory Consultation.fromJson(Map<String, dynamic> json) => Consultation(
        id: json['id'] as String,
        date: json['date'] as String,
        notes: json['notes'] as String?,
        diagnosis: json['diagnosis'] as String?,
        doctorName: json['doctor_name'] as String,
      );
}
