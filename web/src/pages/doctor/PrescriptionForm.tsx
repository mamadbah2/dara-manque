import { useState, useEffect } from "react";
import type { FormEvent } from "react";
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
  const [success, setSuccess] = useState(false);

  useEffect(() => {
    if (!success) return;
    const timer = setTimeout(() => setSuccess(false), 3000);
    return () => clearTimeout(timer);
  }, [success]);

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      const res = await createPrescription(patientId, medications);
      onCreated(res.data);
      setMedications("");
      setSuccess(true);
    } catch {
      setError("Erreur lors de la création de l'ordonnance.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="card">
      <h3 style={{ fontSize: 16, fontWeight: 600, marginBottom: 20 }}>➕ Nouvelle ordonnance</h3>

      {error && <div className="alert alert-error" style={{ marginBottom: 16 }}>{error}</div>}
      {success && (
        <div className="alert alert-success" style={{ marginBottom: 16 }}>
          ✓ Ordonnance créée avec succès.
        </div>
      )}

      <form onSubmit={handleSubmit} style={{ display: "flex", flexDirection: "column", gap: 16 }}>
        <div className="form-group">
          <label className="form-label" htmlFor="medications">Médicaments et posologie</label>
          <textarea
            id="medications"
            className="input"
            value={medications} onChange={e => setMedications(e.target.value)}
            placeholder="Ex : Paracétamol 1g — 3×/jour pendant 5 jours"
            required rows={4}
            style={{ resize: "vertical", lineHeight: 1.5 }}
          />
        </div>
        <div style={{ display: "flex", justifyContent: "flex-end" }}>
          <button
            className="btn btn-primary"
            type="submit" disabled={loading}
          >
            {loading ? "Envoi..." : "Créer l'ordonnance"}
          </button>
        </div>
      </form>
    </div>
  );
}
