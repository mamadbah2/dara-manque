# Alerte allergie à la prescription — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** À la création d'une ordonnance, alerter le médecin (en direct + côté serveur) quand un médicament prescrit entre en conflit avec une allergie connue du patient, cross-réactivité comprise, avec confirmation forcée et trace d'audit.

**Architecture:** Un moteur pur `allergy_rules.py` (classes d'allergènes, fonction sans DB) ; un endpoint de check live + un endpoint de création durci (409 sauf override) côté FastAPI ; une colonne d'audit `allergy_override` (migration Alembic) ; un formulaire React qui appelle le check en debounce et verrouille la soumission derrière une confirmation.

**Tech Stack:** Python 3.12 / FastAPI / SQLAlchemy / Alembic / pytest ; React 18 / TypeScript / Vite / axios.

**Référence spec:** `docs/superpowers/specs/2026-06-10-allergy-alert-design.md`

---

## Structure des fichiers

**Créés :**
- `backend/app/allergy_rules.py` — base de connaissances + `check_allergy_conflicts` (pur, sans DB)
- `backend/alembic/versions/a1b2c3d4e5f6_add_allergy_override.py` — migration colonne d'audit
- `backend/tests/test_allergy.py` — tests unitaires moteur + tests API

**Modifiés :**
- `backend/app/models.py` — colonne `allergy_override`
- `backend/app/schemas.py` — schémas check + champ `override_allergy`
- `backend/app/routers/patients.py` — endpoint check + durcissement create
- `web/src/api/types.ts` — type `AllergyConflict`
- `web/src/api/client.ts` — `checkPrescription` + param override
- `web/src/pages/doctor/PrescriptionForm.tsx` — check live + bandeau + confirmation

---

## Task 1 : Moteur de connaissances `allergy_rules.py`

**Files:**
- Create: `backend/app/allergy_rules.py`
- Test: `backend/tests/test_allergy.py`

- [ ] **Step 1 : Écrire les tests unitaires qui échouent**

Créer `backend/tests/test_allergy.py` :

```python
from app.allergy_rules import check_allergy_conflicts


def test_exact_match():
    conflicts = check_allergy_conflicts("Pénicilline", "Pénicilline 1g")
    assert len(conflicts) == 1
    assert conflicts[0]["allergen_class"] == "Pénicilline"


def test_cross_reactivity_penicillin():
    # Allergique Pénicilline, on prescrit Amoxicilline (même classe, mot différent)
    conflicts = check_allergy_conflicts("Pénicilline", "Amoxicilline 500mg - 3x/jour")
    assert len(conflicts) == 1
    assert conflicts[0]["allergen_class"] == "Pénicilline"
    assert conflicts[0]["medication_term"] == "amoxicilline"


def test_case_and_accent_insensitive():
    conflicts = check_allergy_conflicts("penicilline", "AMOXICILLINE")
    assert len(conflicts) == 1


def test_no_conflict():
    conflicts = check_allergy_conflicts("Pénicilline", "Paracétamol 1g")
    assert conflicts == []


def test_empty_allergies():
    assert check_allergy_conflicts(None, "Amoxicilline") == []
    assert check_allergy_conflicts("", "Amoxicilline") == []


def test_empty_medications():
    assert check_allergy_conflicts("Pénicilline", "") == []


def test_multiple_allergies():
    conflicts = check_allergy_conflicts("Pénicilline, Aspirine", "Ibuprofène 400mg")
    assert len(conflicts) == 1
    assert conflicts[0]["allergen_class"] == "Aspirine/AINS"


def test_no_false_positive_substring():
    # "ains" ne doit PAS matcher dans "bains"
    conflicts = check_allergy_conflicts("Aspirine", "Sels pour bains de bouche")
    assert conflicts == []
```

- [ ] **Step 2 : Lancer les tests pour vérifier l'échec**

Run: `cd backend && source venv/bin/activate && pytest tests/test_allergy.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'app.allergy_rules'`

- [ ] **Step 3 : Implémenter `allergy_rules.py`**

Créer `backend/app/allergy_rules.py` :

```python
import re
import unicodedata

# Chaque classe regroupe TOUS ses termes (nom de classe + médicaments membres +
# orthographes), en forme normalisée (minuscules, sans accents). La cross-réactivité
# tombe d'elle-même : allergie et médicament n'ont qu'à matcher la même classe.
ALLERGEN_CLASSES: dict[str, list[str]] = {
    "Pénicilline": [
        "penicilline", "amoxicilline", "ampicilline", "augmentin",
        "clamoxyl", "oxacilline", "cloxacilline",
    ],
    "Aspirine/AINS": [
        "aspirine", "acide acetylsalicylique", "aspegic", "ibuprofene",
        "diclofenac", "ketoprofene", "ains",
    ],
    "Sulfamides": [
        "sulfamide", "sulfamethoxazole", "bactrim", "cotrimoxazole",
    ],
    "Céphalosporines": [
        "cephalosporine", "ceftriaxone", "cefixime", "cefuroxime",
    ],
    "Codéine": [
        "codeine", "dafalgan codeine", "tramadol",
    ],
    "Iode": [
        "iode", "produit de contraste iode", "povidone iodee", "betadine",
    ],
}


def _normalize(text: str | None) -> str:
    """Minuscules, accents retirés, ponctuation → espaces, espaces compressés."""
    if not text:
        return ""
    text = unicodedata.normalize("NFKD", text.lower())
    text = "".join(c for c in text if not unicodedata.combining(c))
    text = re.sub(r"[^a-z0-9]+", " ", text)
    return text.strip()


def _contains(haystack_norm: str, term: str) -> bool:
    """Correspondance sur mots entiers (gère les termes multi-mots)."""
    term_norm = _normalize(term)
    if not term_norm:
        return False
    return f" {term_norm} " in f" {haystack_norm} "


def check_allergy_conflicts(
    allergies_text: str | None, medications_text: str | None
) -> list[dict]:
    """Retourne la liste des conflits allergie↔médicament détectés."""
    allergies = _normalize(allergies_text)
    meds = _normalize(medications_text)
    if not allergies or not meds:
        return []

    conflicts: list[dict] = []
    for class_name, terms in ALLERGEN_CLASSES.items():
        allergy_term = next((t for t in terms if _contains(allergies, t)), None)
        if allergy_term is None:
            continue
        med_term = next((t for t in terms if _contains(meds, t)), None)
        if med_term is None:
            continue
        conflicts.append({
            "allergen_class": class_name,
            "allergy_term": allergy_term,
            "medication_term": med_term,
        })
    return conflicts
```

- [ ] **Step 4 : Lancer les tests pour vérifier le succès**

Run: `cd backend && source venv/bin/activate && pytest tests/test_allergy.py -v`
Expected: PASS (8 tests)

- [ ] **Step 5 : Commit**

```bash
cd /home/mamadbah/projects/dara-manque
git add backend/app/allergy_rules.py backend/tests/test_allergy.py
git commit -m "feat(backend): add allergy cross-reactivity engine"
```

---

## Task 2 : Colonne d'audit + migration Alembic

**Files:**
- Modify: `backend/app/models.py`
- Create: `backend/alembic/versions/a1b2c3d4e5f6_add_allergy_override.py`

- [ ] **Step 1 : Ajouter la colonne au modèle `Prescription`**

Dans `backend/app/models.py`, dans la classe `Prescription`, ajouter la colonne juste après la ligne `status = Column(...)` :

```python
    allergy_override = Column(Text, nullable=True)
```

(`Text` est déjà importé en haut du fichier.)

- [ ] **Step 2 : Créer la migration Alembic à la main**

Créer `backend/alembic/versions/a1b2c3d4e5f6_add_allergy_override.py` :

```python
"""add allergy_override to prescriptions

Revision ID: a1b2c3d4e5f6
Revises: 1f8d319d5fec
Create Date: 2026-06-10

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "a1b2c3d4e5f6"
down_revision: Union[str, Sequence[str], None] = "1f8d319d5fec"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "prescriptions",
        sa.Column("allergy_override", sa.Text(), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("prescriptions", "allergy_override")
```

- [ ] **Step 3 : Appliquer la migration sur la base de dev**

Run: `cd backend && source venv/bin/activate && alembic upgrade head`
Expected: `Running upgrade 1f8d319d5fec -> a1b2c3d4e5f6, add allergy_override to prescriptions` sans erreur.

> Note : les tests pytest n'ont pas besoin de cette migration (ils créent le schéma via `Base.metadata.create_all`, qui voit déjà la nouvelle colonne).

- [ ] **Step 4 : Commit**

```bash
cd /home/mamadbah/projects/dara-manque
git add backend/app/models.py backend/alembic/versions/a1b2c3d4e5f6_add_allergy_override.py
git commit -m "feat(backend): add allergy_override audit column + migration"
```

---

## Task 3 : Schémas Pydantic

**Files:**
- Modify: `backend/app/schemas.py`

- [ ] **Step 1 : Ajouter les schémas et le champ override**

Dans `backend/app/schemas.py`, ajouter ces classes à la fin du fichier :

```python
class AllergyConflict(BaseModel):
    allergen_class: str
    allergy_term: str
    medication_term: str


class AllergyCheckRequest(BaseModel):
    medications: str


class AllergyCheckResponse(BaseModel):
    conflicts: list[AllergyConflict]
```

Puis modifier la classe existante `PrescriptionCreate` pour ajouter le champ override :

```python
class PrescriptionCreate(BaseModel):
    medications: str
    override_allergy: bool = False
```

- [ ] **Step 2 : Vérifier que l'app importe toujours**

Run: `cd backend && source venv/bin/activate && python -c "from app.main import app; print('ok')"`
Expected: `ok`

- [ ] **Step 3 : Commit**

```bash
cd /home/mamadbah/projects/dara-manque
git add backend/app/schemas.py
git commit -m "feat(backend): add allergy check schemas and override field"
```

---

## Task 4 : Endpoint de check live

**Files:**
- Modify: `backend/app/routers/patients.py`
- Test: `backend/tests/test_allergy.py`

- [ ] **Step 1 : Écrire les tests API du check qui échouent**

Ajouter à la fin de `backend/tests/test_allergy.py` :

```python
def test_check_endpoint_detects_cross_reactivity(client, patient, doctor, doctor_token):
    res = client.post(
        f"/patients/{patient.id}/prescriptions/check",
        json={"medications": "Amoxicilline 500mg"},
        headers={"Authorization": f"Bearer {doctor_token}"},
    )
    assert res.status_code == 200
    conflicts = res.json()["conflicts"]
    assert len(conflicts) == 1
    assert conflicts[0]["allergen_class"] == "Pénicilline"


def test_check_endpoint_no_conflict(client, patient, doctor, doctor_token):
    res = client.post(
        f"/patients/{patient.id}/prescriptions/check",
        json={"medications": "Paracétamol 1g"},
        headers={"Authorization": f"Bearer {doctor_token}"},
    )
    assert res.status_code == 200
    assert res.json()["conflicts"] == []


def test_check_endpoint_requires_doctor(client, patient, pharmacist, pharmacist_token):
    res = client.post(
        f"/patients/{patient.id}/prescriptions/check",
        json={"medications": "Amoxicilline"},
        headers={"Authorization": f"Bearer {pharmacist_token}"},
    )
    assert res.status_code == 403


def test_check_endpoint_patient_not_found(client, doctor, doctor_token):
    res = client.post(
        "/patients/9999/prescriptions/check",
        json={"medications": "Amoxicilline"},
        headers={"Authorization": f"Bearer {doctor_token}"},
    )
    assert res.status_code == 404
```

- [ ] **Step 2 : Lancer pour vérifier l'échec**

Run: `cd backend && source venv/bin/activate && pytest tests/test_allergy.py -k check_endpoint -v`
Expected: FAIL — 404 « Not Found » sur la route (endpoint inexistant) pour les cas attendant 200/403.

- [ ] **Step 3 : Implémenter l'endpoint**

Dans `backend/app/routers/patients.py`, mettre à jour les imports en tête :

```python
from ..schemas import (
    PatientResponse, ConsultationResponse, PrescriptionResponse,
    PrescriptionCreate, AllergyCheckRequest, AllergyCheckResponse, AllergyConflict,
)
from ..allergy_rules import check_allergy_conflicts
```

Puis ajouter cet endpoint (le placer juste avant la route `POST /{patient_id}/prescriptions`) :

```python
@router.post("/{patient_id}/prescriptions/check", response_model=AllergyCheckResponse)
def check_prescription(
    patient_id: int,
    body: AllergyCheckRequest,
    db: Session = Depends(get_db),
    doctor: User = Depends(require_doctor),
):
    patient = db.query(Patient).filter(Patient.id == patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    conflicts = check_allergy_conflicts(patient.allergies, body.medications)
    return AllergyCheckResponse(
        conflicts=[AllergyConflict(**c) for c in conflicts]
    )
```

- [ ] **Step 4 : Lancer pour vérifier le succès**

Run: `cd backend && source venv/bin/activate && pytest tests/test_allergy.py -k check_endpoint -v`
Expected: PASS (4 tests)

- [ ] **Step 5 : Commit**

```bash
cd /home/mamadbah/projects/dara-manque
git add backend/app/routers/patients.py backend/tests/test_allergy.py
git commit -m "feat(backend): add live allergy check endpoint"
```

---

## Task 5 : Durcir la création d'ordonnance (409 + audit)

**Files:**
- Modify: `backend/app/routers/patients.py`
- Test: `backend/tests/test_allergy.py`

- [ ] **Step 1 : Écrire les tests de création durcie qui échouent**

Ajouter à la fin de `backend/tests/test_allergy.py` :

```python
def test_create_blocked_on_conflict(client, patient, doctor, doctor_token, db):
    from app.models import Prescription
    res = client.post(
        f"/patients/{patient.id}/prescriptions",
        json={"medications": "Amoxicilline 500mg"},
        headers={"Authorization": f"Bearer {doctor_token}"},
    )
    assert res.status_code == 409
    assert res.json()["detail"]["conflicts"][0]["allergen_class"] == "Pénicilline"
    # Aucune ordonnance ne doit avoir été créée
    assert db.query(Prescription).count() == 0


def test_create_allowed_with_override(client, patient, doctor, doctor_token, db):
    from app.models import Prescription
    res = client.post(
        f"/patients/{patient.id}/prescriptions",
        json={"medications": "Amoxicilline 500mg", "override_allergy": True},
        headers={"Authorization": f"Bearer {doctor_token}"},
    )
    assert res.status_code == 201
    p = db.query(Prescription).one()
    assert p.allergy_override is not None
    assert "amoxicilline" in p.allergy_override


def test_create_no_conflict_succeeds(client, patient, doctor, doctor_token, db):
    from app.models import Prescription
    res = client.post(
        f"/patients/{patient.id}/prescriptions",
        json={"medications": "Paracétamol 1g"},
        headers={"Authorization": f"Bearer {doctor_token}"},
    )
    assert res.status_code == 201
    p = db.query(Prescription).one()
    assert p.allergy_override is None
```

- [ ] **Step 2 : Lancer pour vérifier l'échec**

Run: `cd backend && source venv/bin/activate && pytest tests/test_allergy.py -k create -v`
Expected: FAIL — la création renvoie 201 sans conflit détecté (`test_create_blocked_on_conflict` attend 409), `allergy_override` inexistant/None.

- [ ] **Step 3 : Implémenter le durcissement**

Dans `backend/app/routers/patients.py`, remplacer entièrement la fonction `create_prescription` existante par :

```python
@router.post("/{patient_id}/prescriptions", response_model=PrescriptionResponse, status_code=201)
def create_prescription(
    patient_id: int,
    body: PrescriptionCreate,
    db: Session = Depends(get_db),
    doctor: User = Depends(require_doctor),
):
    patient = db.query(Patient).filter(Patient.id == patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    conflicts = check_allergy_conflicts(patient.allergies, body.medications)
    if conflicts and not body.override_allergy:
        raise HTTPException(status_code=409, detail={"conflicts": conflicts})

    override_note = None
    if conflicts:
        override_note = "; ".join(
            f"{c['allergen_class']}: {c['medication_term']}" for c in conflicts
        )

    prescription = Prescription(
        id=uuid.uuid4(), patient_id=patient_id, doctor_id=doctor.id,
        created_at=datetime.utcnow(), medications=body.medications,
        status=PrescriptionStatus.active, allergy_override=override_note,
    )
    db.add(prescription)
    db.commit()
    db.refresh(prescription)
    return PrescriptionResponse(
        id=prescription.id, created_at=prescription.created_at,
        medications=prescription.medications, status=prescription.status,
        doctor_name=doctor.full_name,
    )
```

- [ ] **Step 4 : Lancer pour vérifier le succès + toute la suite backend**

Run: `cd backend && source venv/bin/activate && pytest tests/ -v`
Expected: PASS — les 16 tests d'origine + les nouveaux tests allergie (tous verts).

- [ ] **Step 5 : Commit**

```bash
cd /home/mamadbah/projects/dara-manque
git add backend/app/routers/patients.py backend/tests/test_allergy.py
git commit -m "feat(backend): block conflicting prescriptions unless overridden, record audit"
```

---

## Task 6 : Client web (types + appels API)

**Files:**
- Modify: `web/src/api/types.ts`
- Modify: `web/src/api/client.ts`

- [ ] **Step 1 : Ajouter le type `AllergyConflict`**

Dans `web/src/api/types.ts`, ajouter à la fin :

```ts
export interface AllergyConflict {
  allergen_class: string;
  allergy_term: string;
  medication_term: string;
}
```

- [ ] **Step 2 : Ajouter `checkPrescription` et le param override**

Dans `web/src/api/client.ts`, mettre à jour l'import de types en tête :

```ts
import type { AuthResponse, Patient, Consultation, Prescription, AllergyConflict } from "./types";
```

Remplacer la ligne `createPrescription` existante par :

```ts
export const createPrescription = (patientId: number, medications: string, overrideAllergy = false) =>
  api.post<Prescription>(`/patients/${patientId}/prescriptions`, {
    medications,
    override_allergy: overrideAllergy,
  });

export const checkPrescription = (patientId: number, medications: string) =>
  api.post<{ conflicts: AllergyConflict[] }>(
    `/patients/${patientId}/prescriptions/check`,
    { medications },
  );
```

- [ ] **Step 3 : Vérifier la compilation TypeScript**

Run: `cd web && npm run build 2>&1 | tail -5`
Expected: `✓ built in …` sans erreur.

- [ ] **Step 4 : Commit**

```bash
cd /home/mamadbah/projects/dara-manque
git add web/src/api/types.ts web/src/api/client.ts
git commit -m "feat(web): add allergy check API client and override param"
```

---

## Task 7 : Formulaire avec check live + confirmation

**Files:**
- Modify: `web/src/pages/doctor/PrescriptionForm.tsx`

- [ ] **Step 1 : Remplacer entièrement `web/src/pages/doctor/PrescriptionForm.tsx`**

```tsx
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
        setConflicts(err.response.data.detail.conflicts);
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
          {conflicts.map((c, i) => (
            <div key={i} style={{ fontSize: 13 }}>
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
```

- [ ] **Step 2 : Vérifier le build**

Run: `cd web && npm run build 2>&1 | tail -5`
Expected: `✓ built in …` sans erreur TypeScript.

- [ ] **Step 3 : Commit**

```bash
cd /home/mamadbah/projects/dara-manque
git add web/src/pages/doctor/PrescriptionForm.tsx
git commit -m "feat(web): live allergy alert and override confirmation in prescription form"
```

---

## Task 8 : Vérification end-to-end + push

**Files:** aucun (validation)

- [ ] **Step 1 : Suite backend complète**

Run: `cd backend && source venv/bin/activate && pytest tests/ -v`
Expected: tous les tests verts (16 d'origine + ~15 allergie).

- [ ] **Step 2 : Build web final**

Run: `cd web && npm run build 2>&1 | tail -5`
Expected: `✓ built in …` sans erreur.

- [ ] **Step 3 : Démo manuelle (optionnelle mais recommandée)**

1. Démarrer le backend : `cd backend && source venv/bin/activate && fastapi dev app/main.py`
2. Démarrer le web : `cd web && npm run dev`
3. Se connecter `doctor@dara.com / password123`, rechercher patient `1001`.
4. Dans « Nouvelle ordonnance », taper `Amoxicilline 500mg`.
   - Attendu : bandeau rouge « ⚠ Risque d'allergie détecté — Pénicilline : … amoxicilline », bouton verrouillé.
5. Cocher « Je confirme prescrire malgré l'allergie » → bouton actif → créer → succès.
6. Taper `Paracétamol 1g` → aucun bandeau, création directe.

- [ ] **Step 4 : Push GitHub**

```bash
cd /home/mamadbah/projects/dara-manque && git push origin master
```
Expected: `master -> master` sans erreur.

---

## Hors périmètre (rappel)
Interactions médicament-médicament, app mobile Flutter, UI d'édition de la base de connaissances. Voir spec pour la justification.
