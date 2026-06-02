import { useState, FormEvent } from "react";
import { createPrescription } from "../../api/client";
import type { Prescription } from "../../api/types";

interface Props {
  patientId: number;
  onCreated: (p: Prescription) => void;
}

export default function PrescriptionForm({ patientId, onCreated }: Props) {
  const [medications, setMedications] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      const res = await createPrescription(patientId, medications);
      onCreated(res.data);
      setMedications("");
    } catch {
      setError("Erreur lors de la création de l'ordonnance.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <form onSubmit={handleSubmit} style={{ marginTop: 16 }}>
      <h3>Nouvelle ordonnance</h3>
      {error && <p style={{ color: "red" }}>{error}</p>}
      <textarea
        value={medications} onChange={e => setMedications(e.target.value)}
        placeholder="Ex: Paracetamol 1g - 3x/jour"
        required rows={4}
        style={{ width: "100%", padding: 8, margin: "8px 0", border: "1px solid #ccc", borderRadius: 4 }}
      />
      <button
        type="submit" disabled={loading}
        style={{ padding: "8px 20px", background: "#1a73e8", color: "#fff", border: "none", borderRadius: 4 }}
      >
        {loading ? "Envoi..." : "Créer l'ordonnance"}
      </button>
    </form>
  );
}
