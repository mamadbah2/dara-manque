export interface Patient {
  id: number;
  full_name: string;
  date_of_birth: string | null;
  allergies: string | null;
  chronic_conditions: string | null;
  card_uid?: string | null;
}

export interface PatientCreate {
  full_name: string;
  date_of_birth?: string | null;
  allergies?: string | null;
  chronic_conditions?: string | null;
  card_uid?: string | null;
}

export interface LastScan {
  seq: number;
  uid: string | null;
  known: boolean;
  patient: Patient | null;
}

export interface Consultation {
  id: string;
  date: string;
  notes: string | null;
  diagnosis: string | null;
  doctor_name: string;
}

export interface Prescription {
  id: string;
  created_at: string;
  medications: string;
  status: "active" | "treated";
  doctor_name: string;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
  role: "doctor" | "pharmacist";
}

export interface AllergyConflict {
  allergen_class: string;
  allergy_term: string;
  medication_term: string;
}

export interface AffluencePoint {
  date: string;
  patients: number;
}

export interface ForecastPoint {
  date: string;
  predicted_patients: number;
}

export interface AffluenceResponse {
  history: AffluencePoint[];
  forecast: ForecastPoint[];
  kpis: { peak: number; peak_date: string; average: number };
}

export interface FraudSuspect {
  patient: string;
  visites: number;
  medecins_distincts: number;
  hopitaux_distincts: number;
  medicaments_distincts: number;
  score: number;
}

export interface FraudResponse {
  total: number;
  suspects: FraudSuspect[];
}
