import { useEffect, useState } from "react";
import { getPatient, getConsultations, getPrescriptions } from "../../api/client";
import type { Patient, Consultation, Prescription } from "../../api/types";
import PrescriptionForm from "./PrescriptionForm";

interface Props { patientId: number; onBack: () => void; }

function initials(name: string) {
  return name.split(" ").slice(0, 2).map(w => w[0]).join("").toUpperCase();
}

function formatDate(iso: string) {
  return new Date(iso).toLocaleDateString("fr-FR", { day: "numeric", month: "long", year: "numeric" });
}

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

  if (error) return (
    <div>
      <button className="btn btn-ghost btn-sm" onClick={onBack} style={{ marginBottom: 16 }}>← Retour</button>
      <div className="alert alert-error">{error}</div>
    </div>
  );

  if (!patient) return (
    <div style={{ textAlign: "center", padding: 60, color: "var(--text-muted)" }}>
      Chargement du dossier patient…
    </div>
  );

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 24 }}>
      <button className="btn btn-ghost btn-sm" onClick={onBack} style={{ alignSelf: "flex-start" }}>
        ← Retour à la recherche
      </button>

      {/* En-tête patient */}
      <div className="card" style={{ display: "flex", alignItems: "center", gap: 20 }}>
        <div className="avatar" style={{ width: 56, height: 56, fontSize: 20 }}>
          {initials(patient.full_name)}
        </div>
        <div style={{ flex: 1 }}>
          <h2 style={{ fontSize: 20, fontWeight: 700 }}>{patient.full_name}</h2>
          <div className="flex gap-2" style={{ marginTop: 8, flexWrap: "wrap" }}>
            <span className="badge badge-info">ID {patient.id}</span>
            {patient.date_of_birth && (
              <span className="badge badge-info">
                {new Date().getFullYear() - new Date(patient.date_of_birth).getFullYear()} ans
              </span>
            )}
            {patient.allergies && (
              <span className="badge" style={{ background: "#FEF2F2", color: "#DC2626" }}>
                ⚠ {patient.allergies}
              </span>
            )}
            {patient.chronic_conditions && (
              <span className="badge badge-info">{patient.chronic_conditions}</span>
            )}
          </div>
        </div>
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 24 }}>
        {/* Consultations */}
        <div className="card" style={{ padding: 20 }}>
          <h3 style={{ fontSize: 16, fontWeight: 600, marginBottom: 16 }}>
            Consultations <span className="text-muted">({consultations.length})</span>
          </h3>
          {consultations.length === 0 ? (
            <p className="text-muted" style={{ textAlign: "center", padding: "20px 0" }}>
              Aucune consultation enregistrée.
            </p>
          ) : (
            <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
              {consultations.map(c => (
                <div key={c.id} style={{
                  padding: 12, borderRadius: 8,
                  border: "1px solid var(--border)", background: "var(--bg)",
                }}>
                  <p className="text-sm text-muted">{formatDate(c.date)}</p>
                  {c.diagnosis && <p style={{ fontWeight: 600, marginTop: 4 }}>{c.diagnosis}</p>}
                  {c.notes && <p className="text-sm text-muted" style={{ marginTop: 4 }}>{c.notes}</p>}
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Ordonnances actives */}
        <div className="card" style={{ padding: 20 }}>
          <h3 style={{ fontSize: 16, fontWeight: 600, marginBottom: 16 }}>
            Ordonnances actives <span className="text-muted">({prescriptions.length})</span>
          </h3>
          {prescriptions.length === 0 ? (
            <p className="text-muted" style={{ textAlign: "center", padding: "20px 0" }}>
              Aucune ordonnance active.
            </p>
          ) : (
            <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
              {prescriptions.map(p => (
                <div key={p.id} style={{
                  padding: 12, borderRadius: 8,
                  border: "1px solid var(--border)", background: "var(--bg)",
                }}>
                  <div className="flex justify-between items-center" style={{ marginBottom: 8 }}>
                    <p className="text-sm text-muted">{formatDate(p.created_at)}</p>
                    <span className="badge badge-active">● Active</span>
                  </div>
                  <p style={{ fontSize: 14 }}>{p.medications}</p>
                  <p className="text-sm text-muted" style={{ marginTop: 4 }}>Dr. {p.doctor_name}</p>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      <PrescriptionForm patientId={patientId} onCreated={p => setPrescriptions(prev => [...prev, p])} />
    </div>
  );
}
