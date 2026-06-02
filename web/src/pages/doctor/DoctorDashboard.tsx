import { useState, type FormEvent } from "react";
import PatientRecord from "./PatientRecord";
import { useAuth } from "../../hooks/useAuth";

export default function DoctorDashboard() {
  const { signOut } = useAuth();
  const [inputId, setInputId] = useState("");
  const [patientId, setPatientId] = useState<number | null>(null);

  function handleSearch(e: FormEvent) {
    e.preventDefault();
    const id = parseInt(inputId, 10);
    if (!isNaN(id)) setPatientId(id);
  }

  return (
    <div style={{ maxWidth: 800, margin: "0 auto", padding: 24 }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 24 }}>
        <h1 style={{ fontSize: 20 }}>Espace Médecin</h1>
        <button onClick={signOut} style={{ padding: "6px 12px", border: "1px solid #ccc", borderRadius: 4, background: "#fff" }}>
          Déconnexion
        </button>
      </div>

      {!patientId ? (
        <form onSubmit={handleSearch} style={{ display: "flex", gap: 8 }}>
          <input
            type="number" value={inputId} onChange={e => setInputId(e.target.value)}
            placeholder="ID du patient (ex: 1001)"
            required
            style={{ flex: 1, padding: 8, border: "1px solid #ccc", borderRadius: 4 }}
          />
          <button type="submit" style={{ padding: "8px 16px", background: "#1a73e8", color: "#fff", border: "none", borderRadius: 4 }}>
            Rechercher
          </button>
        </form>
      ) : (
        <PatientRecord patientId={patientId} onBack={() => setPatientId(null)} />
      )}
    </div>
  );
}
