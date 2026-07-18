import { useState } from "react";
import type { FormEvent } from "react";
import axios from "axios";
import { createPatient } from "../../api/client";

interface Props {
  /** UID read from the card that isn't linked to any patient yet. */
  uid: string;
  onCreated: (patientId: number) => void;
  onCancel: () => void;
}

/**
 * New-patient enrollment triggered by an unknown card. The doctor fills in the
 * dossier; the scanned UID is linked to it (POST /patients). Once created the
 * card is recognized on subsequent scans.
 */
export default function EnrollPatientForm({ uid, onCreated, onCancel }: Props) {
  const [fullName, setFullName] = useState("");
  const [dob, setDob] = useState("");
  const [allergies, setAllergies] = useState("");
  const [chronic, setChronic] = useState("");
  const [error, setError] = useState("");
  const [saving, setSaving] = useState(false);

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    setError("");
    setSaving(true);
    try {
      const res = await createPatient({
        full_name: fullName.trim(),
        date_of_birth: dob || null,
        allergies: allergies.trim() || null,
        chronic_conditions: chronic.trim() || null,
        card_uid: uid,
      });
      onCreated(res.data.id);
    } catch (err) {
      if (axios.isAxiosError(err) && err.response?.status === 409) {
        setError("Cette carte est déjà associée à un patient.");
      } else {
        setError("Erreur lors de l'enregistrement du patient.");
      }
      setSaving(false);
    }
  }

  return (
    <div style={{ display: "flex", justifyContent: "center", paddingTop: 20 }}>
      <div className="card" style={{ width: "100%", maxWidth: 520 }}>
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
            <span style={{ fontSize: 22 }}>🆕</span>
          </div>
          <h2 style={{ fontSize: 18, fontWeight: 600 }}>Nouveau patient</h2>
          <p className="text-muted" style={{ marginTop: 4 }}>
            Carte non reconnue — enregistrez le patient pour lier cette carte.
          </p>
          <div className="badge badge-info" style={{ marginTop: 10 }}>
            Carte : {uid}
          </div>
        </div>

        <form onSubmit={handleSubmit} style={{ display: "flex", flexDirection: "column", gap: 14 }}>
          <label style={{ display: "flex", flexDirection: "column", gap: 6 }}>
            <span className="text-sm">Nom complet *</span>
            <input
              className="input"
              value={fullName}
              onChange={(e) => setFullName(e.target.value)}
              placeholder="Ex : Awa Ndiaye"
              required
            />
          </label>

          <label style={{ display: "flex", flexDirection: "column", gap: 6 }}>
            <span className="text-sm">Date de naissance</span>
            <input className="input" type="date" value={dob} onChange={(e) => setDob(e.target.value)} />
          </label>

          <label style={{ display: "flex", flexDirection: "column", gap: 6 }}>
            <span className="text-sm">Allergies</span>
            <input
              className="input"
              value={allergies}
              onChange={(e) => setAllergies(e.target.value)}
              placeholder="Ex : Pénicilline"
            />
          </label>

          <label style={{ display: "flex", flexDirection: "column", gap: 6 }}>
            <span className="text-sm">Pathologies chroniques</span>
            <input
              className="input"
              value={chronic}
              onChange={(e) => setChronic(e.target.value)}
              placeholder="Ex : Diabète type 2"
            />
          </label>

          {error && <div className="alert alert-error">{error}</div>}

          <div style={{ display: "flex", gap: 10, marginTop: 4 }}>
            <button type="button" className="btn btn-ghost" onClick={onCancel} disabled={saving}>
              Annuler
            </button>
            <button type="submit" className="btn btn-primary" style={{ flex: 1 }} disabled={saving}>
              {saving ? "Enregistrement…" : "Enregistrer et lier la carte"}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
