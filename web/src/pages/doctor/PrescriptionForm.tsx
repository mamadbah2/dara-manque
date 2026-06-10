import { useState, useEffect } from "react";
import type { FormEvent } from "react";
import axios from "axios";
import { createPrescription, checkPrescription } from "../../api/client";
import type { Prescription, AllergyConflict } from "../../api/types";

interface Props {
  patientId: number;
  onCreated: (p: Prescription) => void;
}

export default function PrescriptionForm({ patientId, onCreated }: Props) {
  const [medications, setMedications] = useState("");
  const [conflicts, setConflicts] = useState<AllergyConflict[]>([]);
  const [override, setOverride] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState(false);

  // Check live (debounce 400ms) à chaque modification du texte
  useEffect(() => {
    if (!medications.trim()) {
      setConflicts([]);
      return;
    }
    const handle = setTimeout(async () => {
      try {
        const res = await checkPrescription(patientId, medications);
        setConflicts(res.data.conflicts);
      } catch {
        setConflicts([]);
      }
    }, 400);
    return () => clearTimeout(handle);
  }, [medications, patientId]);

  useEffect(() => {
    if (!success) return;
    const timer = setTimeout(() => setSuccess(false), 3000);
    return () => clearTimeout(timer);
  }, [success]);

  const blocked = conflicts.length > 0 && !override;

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    if (blocked) return;
    setError("");
    setLoading(true);
    try {
      const res = await createPrescription(patientId, medications, override);
      onCreated(res.data);
      setMedications("");
      setConflicts([]);
      setOverride(false);
      setSuccess(true);
    } catch (err) {
      if (axios.isAxiosError(err) && err.response?.status === 409) {
        const raw = err.response.data?.detail?.conflicts;
        if (Array.isArray(raw)) setConflicts(raw);
        setError("Conflit d'allergie détecté — confirmez pour prescrire malgré tout.");
      } else {
        setError("Erreur lors de la création de l'ordonnance.");
      }
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

      {conflicts.length > 0 && (
        <div className="alert alert-error" style={{ marginBottom: 16 }}>
          <strong style={{ display: "block", marginBottom: 6 }}>⚠ Risque d'allergie détecté</strong>
          {conflicts.map((c) => (
            <div key={`${c.allergen_class}-${c.medication_term}`} style={{ fontSize: 13 }}>
              <strong>{c.allergen_class}</strong> : l'ordonnance contient <em>{c.medication_term}</em>.
            </div>
          ))}
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

        {conflicts.length > 0 && (
          <label className="flex items-center gap-2" style={{ fontSize: 14, color: "var(--danger)" }}>
            <input
              type="checkbox"
              checked={override}
              onChange={e => setOverride(e.target.checked)}
            />
            Je confirme prescrire malgré l'allergie
          </label>
        )}

        <div style={{ display: "flex", justifyContent: "flex-end" }}>
          <button
            className="btn btn-primary"
            type="submit" disabled={loading || blocked}
          >
            {loading ? "Envoi..." : "Créer l'ordonnance"}
          </button>
        </div>
      </form>
    </div>
  );
}
