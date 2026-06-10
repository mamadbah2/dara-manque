import axios from "axios";
import type { AuthResponse, Patient, Consultation, Prescription, AllergyConflict } from "./types";

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL ?? "http://localhost:9000",
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem("token");
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

export const login = (email: string, password: string) =>
  api.post<AuthResponse>("/auth/login", { email, password });

export const getPatient = (id: number) =>
  api.get<Patient>(`/patients/${id}`);

export const getConsultations = (patientId: number) =>
  api.get<Consultation[]>(`/patients/${patientId}/consultations`);

export const getPrescriptions = (patientId: number) =>
  api.get<Prescription[]>(`/patients/${patientId}/prescriptions`);

export const createPrescription = (patientId: number, medications: string, overrideAllergy = false) =>
  api.post<Prescription>(`/patients/${patientId}/prescriptions`, {
    medications,
    override_allergy: overrideAllergy,
  });

export const checkPrescription = (patientId: number, medications: string) =>
  api.post<{ conflicts: AllergyConflict[] }>(
    `/patients/${patientId}/prescriptions/check`,
    { medications },
  );

export const treatPrescription = (prescriptionId: string) =>
  api.patch<Prescription>(`/prescriptions/${prescriptionId}/treat`);
