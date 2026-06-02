export interface Patient {
  id: number;
  full_name: string;
  date_of_birth: string | null;
  allergies: string | null;
  chronic_conditions: string | null;
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
