import { useState, type FormEvent } from "react";
import { getPatient, getPrescriptions, treatPrescription } from "../../api/client";
import type { Patient, Prescription } from "../../api/types";
import { useAuth } from "../../hooks/useAuth";

export default function PharmacistDashboard() {
  const { signOut } = useAuth();
  const [inputId, setInputId] = useState("");
  const [patient, setPatient] = useState<Patient | null>(null);
  const [prescriptions, setPrescriptions] = useState<Prescription[]>([]);
  const [error, setError] = useState("");

  async function handleSearch(e: FormEvent) {
    e.preventDefault();
    setError("");
    const id = parseInt(inputId, 10);
    if (isNaN(id)) return;
    try {
      const [p, pr] = await Promise.all([getPatient(id), getPrescriptions(id)]);
      setPatient(p.data);
      setPrescriptions(pr.data);
    } catch {
      setError("Patient introuvable.");
      setPatient(null);
      setPrescriptions([]);
    }
  }

  async function handleTreat(prescriptionId: string) {
    try {
      await treatPrescription(prescriptionId);
      setPrescriptions(prev => prev.filter(p => p.id !== prescriptionId));
    } catch {
      setError("Erreur lors du traitement de l'ordonnance.");
    }
  }

  return (
    <div style={{ maxWidth: 800, margin: "0 auto", padding: 24 }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 24 }}>
        <h1 style={{ fontSize: 20 }}>Espace Pharmacien</h1>
        <button onClick={signOut} style={{ padding: "6px 12px", border: "1px solid #ccc", borderRadius: 4, background: "#fff" }}>
          Déconnexion
        </button>
      </div>

      <form onSubmit={handleSearch} style={{ display: "flex", gap: 8, marginBottom: 24 }}>
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

      {error && <p style={{ color: "red", marginBottom: 12 }}>{error}</p>}

      {patient && (
        <div>
          <h2>{patient.full_name}</h2>
          <p style={{ color: "#555", fontSize: 14 }}>
            Allergies : {patient.allergies ?? "Aucune"}
          </p>

          <h3 style={{ marginTop: 20 }}>Ordonnances actives ({prescriptions.length})</h3>
          {prescriptions.length === 0 ? (
            <p>Aucune ordonnance active.</p>
          ) : (
            <ul style={{ listStyle: "none", padding: 0 }}>
              {prescriptions.map(p => (
                <li key={p.id} style={{ background: "#fff", padding: 16, borderRadius: 6, marginBottom: 12, boxShadow: "0 1px 3px rgba(0,0,0,.08)" }}>
                  <p style={{ fontSize: 13, color: "#888" }}>
                    Prescrit le {new Date(p.created_at).toLocaleDateString("fr-FR")} par {p.doctor_name}
                  </p>
                  <pre style={{ margin: "8px 0", fontSize: 14 }}>{p.medications}</pre>
                  <button
                    onClick={() => handleTreat(p.id)}
                    style={{ padding: "6px 14px", background: "#34a853", color: "#fff", border: "none", borderRadius: 4 }}
                  >
                    Marquer comme traitée
                  </button>
                </li>
              ))}
            </ul>
          )}
        </div>
      )}
    </div>
  );
}
