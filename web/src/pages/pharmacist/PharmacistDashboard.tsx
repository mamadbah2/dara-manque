import { useState } from "react";
import type { FormEvent } from "react";
import { getPatient, getPrescriptions, treatPrescription } from "../../api/client";
import type { Patient, Prescription } from "../../api/types";
import AppShell from "../../components/AppShell";

function formatDate(iso: string) {
  return new Date(iso).toLocaleDateString("fr-FR", { day: "numeric", month: "long", year: "numeric" });
}

export default function PharmacistDashboard() {
  const [inputId, setInputId] = useState("");
  const [patient, setPatient] = useState<Patient | null>(null);
  const [prescriptions, setPrescriptions] = useState<Prescription[]>([]);
  const [treating, setTreating] = useState<string | null>(null);
  const [error, setError] = useState("");

  async function handleSearch(e: FormEvent) {
    e.preventDefault();
    setError("");
    setPatient(null);
    setPrescriptions([]);
    const id = parseInt(inputId, 10);
    if (isNaN(id)) return;
    try {
      const [p, pr] = await Promise.all([getPatient(id), getPrescriptions(id)]);
      setPatient(p.data);
      setPrescriptions(pr.data);
    } catch {
      setError("Patient introuvable.");
    }
  }

  async function handleTreat(prescriptionId: string) {
    setTreating(prescriptionId);
    try {
      await treatPrescription(prescriptionId);
      setPrescriptions(prev => prev.filter(p => p.id !== prescriptionId));
    } catch {
      setError("Erreur lors du traitement de l'ordonnance.");
    } finally {
      setTreating(null);
    }
  }

  return (
    <AppShell role="pharmacist">
      {/* Recherche */}
      <div className="card" style={{ marginBottom: 24 }}>
        <h2 style={{ fontSize: 17, fontWeight: 600, marginBottom: 16 }}>Rechercher un patient</h2>
        <form onSubmit={handleSearch} style={{ display: "flex", gap: 10 }}>
          <input
            className="input"
            type="number" value={inputId} onChange={e => setInputId(e.target.value)}
            placeholder="N° de carte patient (ex : 1001)" required
          />
          <button className="btn btn-primary" type="submit" style={{ whiteSpace: "nowrap" }}>
            Rechercher
          </button>
        </form>
      </div>

      {error && <div className="alert alert-error" style={{ marginBottom: 16 }}>{error}</div>}

      {patient && (
        <div>
          <div className="card" style={{ marginBottom: 20, display: "flex", alignItems: "center", gap: 16 }}>
            <div className="avatar">
              {patient.full_name.split(" ").slice(0, 2).map((w: string) => w[0]).join("").toUpperCase()}
            </div>
            <div>
              <h3 style={{ fontWeight: 700, fontSize: 18 }}>{patient.full_name}</h3>
              {patient.allergies && (
                <p style={{ fontSize: 13, color: "var(--danger)", marginTop: 4 }}>
                  ⚠ Allergies : {patient.allergies}
                </p>
              )}
            </div>
          </div>

          <h3 style={{ fontWeight: 600, marginBottom: 12 }}>
            Ordonnances actives{" "}
            <span className="text-muted">({prescriptions.length})</span>
          </h3>

          {prescriptions.length === 0 ? (
            <div className="card" style={{ textAlign: "center", padding: 32 }}>
              <p style={{ fontSize: 24, marginBottom: 8 }}>🎉</p>
              <p className="text-muted">Aucune ordonnance active pour ce patient.</p>
            </div>
          ) : (
            <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
              {prescriptions.map(p => (
                <div className="card-sm" key={p.id} style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", gap: 16 }}>
                  <div style={{ flex: 1 }}>
                    <div className="flex items-center gap-2" style={{ marginBottom: 8 }}>
                      <span className="badge badge-active">● Active</span>
                      <span className="text-sm text-muted">Prescrite le {formatDate(p.created_at)}</span>
                    </div>
                    <p style={{ fontWeight: 600, marginBottom: 4 }}>{p.medications}</p>
                    <p className="text-sm text-muted">Dr. {p.doctor_name}</p>
                  </div>
                  <button
                    className="btn btn-outline btn-sm"
                    onClick={() => handleTreat(p.id)}
                    disabled={treating === p.id}
                    style={{ whiteSpace: "nowrap", flexShrink: 0 }}
                  >
                    {treating === p.id ? "..." : "✓ Marquer traitée"}
                  </button>
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </AppShell>
  );
}
