import { useState } from "react";
import type { FormEvent } from "react";
import PatientRecord from "./PatientRecord";
import AppShell from "../../components/AppShell";

export default function DoctorDashboard() {
  const [inputId, setInputId] = useState("");
  const [patientId, setPatientId] = useState<number | null>(null);

  function handleSearch(e: FormEvent) {
    e.preventDefault();
    const id = parseInt(inputId, 10);
    if (!isNaN(id)) setPatientId(id);
  }

  return (
    <AppShell role="doctor">
      {!patientId ? (
        <div style={{ display: "flex", justifyContent: "center", paddingTop: 40 }}>
          <div className="card" style={{ width: "100%", maxWidth: 480 }}>
            <div style={{ textAlign: "center", marginBottom: 24 }}>
              <div style={{
                display: "inline-flex", alignItems: "center", justifyContent: "center",
                width: 48, height: 48, borderRadius: "50%",
                background: "var(--primary-light)", marginBottom: 12,
              }}>
                <span style={{ fontSize: 22 }}>🔍</span>
              </div>
              <h2 style={{ fontSize: 18, fontWeight: 600 }}>Rechercher un patient</h2>
              <p className="text-muted" style={{ marginTop: 4 }}>Entrez le numéro de carte du patient</p>
            </div>
            <form onSubmit={handleSearch} style={{ display: "flex", gap: 10 }}>
              <input
                className="input"
                type="number" value={inputId} onChange={e => setInputId(e.target.value)}
                placeholder="Ex : 1001" required
              />
              <button className="btn btn-primary" type="submit" style={{ whiteSpace: "nowrap" }}>
                Rechercher
              </button>
            </form>
          </div>
        </div>
      ) : (
        <PatientRecord patientId={patientId} onBack={() => { setPatientId(null); setInputId(""); }} />
      )}
    </AppShell>
  );
}
