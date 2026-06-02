import { useEffect, useState } from "react";
import { getPatient, getConsultations, getPrescriptions } from "../../api/client";
import type { Patient, Consultation, Prescription } from "../../api/types";
import PrescriptionForm from "./PrescriptionForm";

interface Props { patientId: number; onBack: () => void; }

export default function PatientRecord({ patientId, onBack }: Props) {
  const [patient, setPatient] = useState<Patient | null>(null);
  const [consultations, setConsultations] = useState<Consultation[]>([]);
  const [prescriptions, setPrescriptions] = useState<Prescription[]>([]);
  const [error, setError] = useState("");

  useEffect(() => {
    Promise.all([
      getPatient(patientId),
      getConsultations(patientId),
      getPrescriptions(patientId),
    ])
      .then(([p, c, pr]) => {
        setPatient(p.data);
        setConsultations(c.data);
        setPrescriptions(pr.data);
      })
      .catch(() => setError("Patient introuvable."));
  }, [patientId]);

  if (error) return <p style={{ color: "red" }}>{error}</p>;
  if (!patient) return <p>Chargement...</p>;

  return (
    <div>
      <button onClick={onBack} style={{ marginBottom: 16 }}>← Retour</button>
      <h2>{patient.full_name}</h2>
      <p><strong>Né(e) le :</strong> {patient.date_of_birth ?? "N/A"}</p>
      <p><strong>Allergies :</strong> {patient.allergies ?? "Aucune"}</p>
      <p><strong>Maladies chroniques :</strong> {patient.chronic_conditions ?? "Aucune"}</p>

      <h3 style={{ marginTop: 24 }}>Consultations ({consultations.length})</h3>
      {consultations.length === 0 ? <p>Aucune consultation.</p> : (
        <ul>
          {consultations.map(c => (
            <li key={c.id} style={{ margin: "8px 0", padding: 8, background: "#fff", borderRadius: 4 }}>
              <strong>{new Date(c.date).toLocaleDateString("fr-FR")}</strong> — {c.diagnosis ?? ""}
              {c.notes && <p style={{ color: "#555", fontSize: 14 }}>{c.notes}</p>}
            </li>
          ))}
        </ul>
      )}

      <h3 style={{ marginTop: 24 }}>Ordonnances actives ({prescriptions.length})</h3>
      {prescriptions.length === 0 ? <p>Aucune ordonnance active.</p> : (
        <ul>
          {prescriptions.map(p => (
            <li key={p.id} style={{ margin: "8px 0", padding: 8, background: "#fff", borderRadius: 4 }}>
              <strong>{new Date(p.created_at).toLocaleDateString("fr-FR")}</strong>
              <pre style={{ marginTop: 4, fontSize: 13 }}>{p.medications}</pre>
            </li>
          ))}
        </ul>
      )}

      <PrescriptionForm patientId={patientId} onCreated={p => setPrescriptions(prev => [...prev, p])} />
    </div>
  );
}
