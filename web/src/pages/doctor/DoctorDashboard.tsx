import { useCallback, useState } from "react";
import type { FormEvent } from "react";
import PatientRecord from "./PatientRecord";
import EnrollPatientForm from "./EnrollPatientForm";
import CardStation from "../../components/CardStation";
import AppShell from "../../components/AppShell";

export default function DoctorDashboard() {
  const [inputId, setInputId] = useState("");
  const [patientId, setPatientId] = useState<number | null>(null);
  const [enrollUid, setEnrollUid] = useState<string | null>(null);

  function handleSearch(e: FormEvent) {
    e.preventDefault();
    const id = parseInt(inputId, 10);
    if (!isNaN(id)) {
      setEnrollUid(null);
      setPatientId(id);
    }
  }

  const handleKnown = useCallback((id: number) => {
    setEnrollUid(null);
    setPatientId(id);
  }, []);

  const handleUnknown = useCallback((uid: string) => {
    setPatientId(null);
    setEnrollUid(uid);
  }, []);

  function reset() {
    setPatientId(null);
    setEnrollUid(null);
    setInputId("");
  }

  return (
    <AppShell role="doctor">
      {patientId ? (
        <PatientRecord patientId={patientId} onBack={reset} />
      ) : enrollUid ? (
        <EnrollPatientForm uid={enrollUid} onCreated={handleKnown} onCancel={reset} />
      ) : (
        <div style={{ display: "flex", flexDirection: "column", gap: 20, maxWidth: 520, margin: "20px auto 0" }}>
          <CardStation onKnown={handleKnown} onUnknown={handleUnknown} />

          <div className="card">
            <div style={{ textAlign: "center", marginBottom: 20 }}>
              <div
                style={{
                  display: "inline-flex",
                  alignItems: "center",
                  justifyContent: "center",
                  width: 48,
                  height: 48,
                  borderRadius: "50%",
                  background: "var(--primary-light)",
                  marginBottom: 12,
                }}
              >
                <span style={{ fontSize: 22 }}>🔍</span>
              </div>
              <h2 style={{ fontSize: 18, fontWeight: 600 }}>Rechercher un patient</h2>
              <p className="text-muted" style={{ marginTop: 4 }}>
                Ou entrez manuellement le numéro de carte
              </p>
            </div>
            <form onSubmit={handleSearch} style={{ display: "flex", gap: 10 }}>
              <input
                className="input"
                type="number"
                value={inputId}
                onChange={(e) => setInputId(e.target.value)}
                placeholder="Ex : 1001"
                required
              />
              <button className="btn btn-primary" type="submit" style={{ whiteSpace: "nowrap" }}>
                Rechercher
              </button>
            </form>
          </div>
        </div>
      )}
    </AppShell>
  );
}
