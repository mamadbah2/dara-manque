# Module « Analytics IA » (Affluence + Fraude) — Plan d'implémentation

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Ajouter un module d'IA visible à Dara Manqué : deux modèles pré-entraînés (prévision d'affluence + détection de fraude) exposés par le backend FastAPI et affichés dans une page « Analytics IA » du web React.

**Architecture:** Les modèles `.pkl` (scikit-learn) tournent en inférence live côté backend, mais sur de petits fichiers de features pré-calculés (générés une fois par un script depuis le dataset Kaggle, non commité). Un module `backend/app/ai/` charge modèles + données au premier appel (cache mémoire) et expose deux endpoints JSON protégés par JWT. Le front ajoute une page avec graphiques Recharts.

**Tech Stack:** FastAPI, scikit-learn 1.9.0, joblib, pandas, numpy (backend) ; React 19, Vite, TypeScript, Recharts, axios (frontend).

## Global Constraints

- **scikit-learn épinglé à `==1.9.0`** — version qui a sérialisé les `.pkl` (`_sklearn_version` = 1.9.0) ; toute autre version peut casser la dé-sérialisation.
- **Ne jamais commiter** le CSV Kaggle brut `healthcare_dataset_2.csv` (8 Mo) ni le modèle `readmission_risk.pkl` (105 Mo).
- **Commits sans `Co-Authored-By`** — convention du repo : chaque commit porte uniquement le dev (mamadbah2).
- **Backend servi sur le port 9000** (le web appelle 9000 ; 8000 est pris par un autre projet).
- **Label « données de démonstration »** obligatoire et visible dans la page Analytics (les chiffres viennent d'un dataset synthétique, pas des vrais patients).
- **Endpoints protégés** par `get_current_user` (tout utilisateur authentifié ; pas de rôle dédié).
- Source de vérité des features des modèles (ordre exact) :
  - Affluence : `["DayOfWeek", "Month", "Day", "Is_Weekend", "Season", "MA7", "Lag_1", "Lag_3", "Lag_7"]`
  - Fraude : `["Patient_Count", "Unique_Doctors", "Unique_Hospitals", "Unique_Medications"]`

---

### Task 1: Dépendances backend + modèles vendorés

**Files:**
- Modify: `backend/requirements.txt`
- Create: `backend/app/ai/__init__.py`
- Create: `backend/app/ai/models/affluence_neural_network.pkl` (copie depuis le zip)
- Create: `backend/app/ai/models/affluence_scaler.pkl`
- Create: `backend/app/ai/models/fraud_isolation_forest.pkl`
- Create: `backend/app/ai/models/fraud_scaler.pkl`
- Modify: `backend/.gitignore` (ou créer `backend/app/ai/data/.gitignore`)
- Test: `backend/tests/test_ai.py`

**Interfaces:**
- Produces: le package importable `app.ai` ; les 4 `.pkl` présents sous `backend/app/ai/models/`.

- [ ] **Step 1: Ajouter les dépendances**

Ajouter à la fin de `backend/requirements.txt` :

```
scikit-learn==1.9.0
joblib>=1.4.0
pandas>=2.2.0
numpy>=1.26.0
```

- [ ] **Step 2: Installer**

Run (depuis `backend/`, venv activé) :
```bash
cd backend && source venv/bin/activate && pip install -r requirements.txt
```
Expected: installation de scikit-learn 1.9.0, pandas, numpy, joblib sans erreur.

- [ ] **Step 3: Copier les 4 modèles depuis le zip**

Extraire le zip dans un dossier temporaire puis copier les 4 fichiers légers (PAS le readmission de 105 Mo) :
```bash
mkdir -p backend/app/ai/models backend/app/ai/data
TMP=$(mktemp -d)
unzip -q -o projet_medical_ia.zip -d "$TMP" \
  "projet_medical_ia/models/affluence_neural_network.pkl" \
  "projet_medical_ia/models/affluence_scaler.pkl" \
  "projet_medical_ia/models/fraud_isolation_forest.pkl" \
  "projet_medical_ia/models/fraud_scaler.pkl"
cp "$TMP"/projet_medical_ia/models/*.pkl backend/app/ai/models/
ls -lh backend/app/ai/models/
```
Expected: 4 fichiers (~90 Ko, 1 Ko, 159 Ko, 1 Ko).

- [ ] **Step 4: Créer le package + ignorer les artefacts lourds**

Créer `backend/app/ai/__init__.py` (fichier vide).

Créer `backend/app/ai/data/.gitignore` avec :
```
# CSV source Kaggle (8 Mo) — jamais commité, extrait du zip à la demande
_source/
healthcare_dataset_2.csv
```

- [ ] **Step 5: Écrire le test de chargement des modèles**

Créer `backend/tests/test_ai.py` :
```python
import joblib
from pathlib import Path

MODELS = Path(__file__).resolve().parent.parent / "app" / "ai" / "models"


def test_all_models_load():
    for name in [
        "affluence_neural_network.pkl",
        "affluence_scaler.pkl",
        "fraud_isolation_forest.pkl",
        "fraud_scaler.pkl",
    ]:
        model = joblib.load(MODELS / name)
        assert model is not None
```

- [ ] **Step 6: Lancer le test (doit passer)**

Run: `cd backend && source venv/bin/activate && pytest tests/test_ai.py::test_all_models_load -v`
Expected: PASS (aucun warning de version incompatible ; si un `InconsistentVersionWarning` apparaît, vérifier que scikit-learn vaut bien 1.9.0).

- [ ] **Step 7: Commit**

```bash
git add backend/requirements.txt backend/app/ai/__init__.py backend/app/ai/models backend/app/ai/data/.gitignore backend/tests/test_ai.py
git commit -m "feat(ai): dépendances scikit-learn et modèles affluence/fraude vendorés"
```

---

### Task 2: Script de préparation des features + CSV générés

**Files:**
- Create: `backend/app/ai/prep_ai_data.py`
- Create: `backend/app/ai/data/affluence_history.csv` (généré)
- Create: `backend/app/ai/data/fraud_features.csv` (généré, ~1,8 Mo, 49 992 lignes)
- Modify: `backend/tests/test_ai.py`

**Interfaces:**
- Consumes: le CSV Kaggle brut (chemin passé en argument), extrait du zip mais non commité.
- Produces: `affluence_history.csv` (colonnes `Date, Patient_Count`, 90 lignes) et `fraud_features.csv` (colonnes `Name, Patient_Count, Unique_Doctors, Unique_Hospitals, Unique_Medications`).

- [ ] **Step 1: Écrire le script de préparation**

Créer `backend/app/ai/prep_ai_data.py` :
```python
"""Génère les CSV de features IA depuis le dataset Kaggle brut.

One-shot, lancé une seule fois par le dev. Le CSV source (8 Mo) n'est PAS
commité — extrais-le de projet_medical_ia.zip.

Usage:
    python -m app.ai.prep_ai_data /chemin/vers/healthcare_dataset_2.csv
"""
import sys
from pathlib import Path

import pandas as pd

_DATA = Path(__file__).parent / "data"


def main(src: str) -> None:
    src_path = Path(src)
    if not src_path.exists():
        print(f"❌ CSV source introuvable : {src_path}")
        sys.exit(1)

    df = pd.read_csv(src_path)
    df.columns = df.columns.str.strip()

    # --- Affluence : comptages d'admissions par jour, 90 derniers jours ---
    df["Date_Admission"] = pd.to_datetime(df["Date of Admission"])
    daily = df.groupby("Date_Admission").size().reset_index(name="Patient_Count")
    daily = daily.set_index("Date_Admission").asfreq("D", fill_value=0).reset_index()
    daily.columns = ["Date", "Patient_Count"]
    daily.tail(90).to_csv(_DATA / "affluence_history.csv", index=False)

    # --- Fraude : agrégats par patient (tous les patients uniques) ---
    grp = df.groupby("Name")
    feats = pd.DataFrame(
        {
            "Patient_Count": grp.size(),
            "Unique_Doctors": grp["Doctor"].nunique(),
            "Unique_Hospitals": grp["Hospital"].nunique(),
            "Unique_Medications": grp["Medication"].nunique(),
        }
    ).reset_index()
    feats.to_csv(_DATA / "fraud_features.csv", index=False)

    print(f"✅ affluence_history.csv ({len(daily.tail(90))} lignes)")
    print(f"✅ fraud_features.csv ({len(feats)} lignes)")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python -m app.ai.prep_ai_data <chemin_csv>")
        sys.exit(1)
    main(sys.argv[1])
```

- [ ] **Step 2: Extraire le CSV source et lancer le script**

```bash
mkdir -p backend/app/ai/data/_source
unzip -q -o projet_medical_ia.zip -d backend/app/ai/data/_source \
  "projet_medical_ia/data/raw/healthcare_dataset_2.csv"
cd backend && source venv/bin/activate && \
  python -m app.ai.prep_ai_data app/ai/data/_source/projet_medical_ia/data/raw/healthcare_dataset_2.csv
```
Expected:
```
✅ affluence_history.csv (90 lignes)
✅ fraud_features.csv (49992 lignes)
```

- [ ] **Step 3: Écrire le test de schéma des CSV**

Ajouter à `backend/tests/test_ai.py` :
```python
import pandas as pd

DATA = Path(__file__).resolve().parent.parent / "app" / "ai" / "data"


def test_feature_csvs_have_expected_schema():
    affluence = pd.read_csv(DATA / "affluence_history.csv")
    assert list(affluence.columns) == ["Date", "Patient_Count"]
    assert len(affluence) > 0

    fraud = pd.read_csv(DATA / "fraud_features.csv")
    assert list(fraud.columns) == [
        "Name",
        "Patient_Count",
        "Unique_Doctors",
        "Unique_Hospitals",
        "Unique_Medications",
    ]
    assert len(fraud) > 0
```

- [ ] **Step 4: Lancer le test (doit passer)**

Run: `cd backend && source venv/bin/activate && pytest tests/test_ai.py::test_feature_csvs_have_expected_schema -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add backend/app/ai/prep_ai_data.py backend/app/ai/data/affluence_history.csv backend/app/ai/data/fraud_features.csv backend/tests/test_ai.py
git commit -m "feat(ai): script de préparation et features affluence/fraude pré-calculées"
```
(Le CSV source de 8 Mo dans `_source/` reste ignoré par le `.gitignore` de Task 1 — vérifier `git status` : il ne doit PAS apparaître.)

---

### Task 3: Moteur d'inférence (`engine.py`)

**Files:**
- Create: `backend/app/ai/engine.py`
- Modify: `backend/tests/test_ai.py`

**Interfaces:**
- Consumes: modèles + CSV de Task 1 & 2.
- Produces:
  - `predict_affluence(horizon: int = 30) -> dict` → `{"history": [{"date": str, "patients": int}], "forecast": [{"date": str, "predicted_patients": int}], "kpis": {"peak": int, "peak_date": str, "average": int}}`
  - `detect_fraud(top: int = 50) -> dict` → `{"total": int, "suspects": [{"patient": str, "visites": int, "medecins_distincts": int, "hopitaux_distincts": int, "medicaments_distincts": int, "score": float}]}`

- [ ] **Step 1: Écrire les tests du moteur**

Ajouter à `backend/tests/test_ai.py` :
```python
from app.ai import engine


def test_predict_affluence_shape():
    result = engine.predict_affluence(horizon=30)
    assert len(result["forecast"]) == 30
    assert all(p["predicted_patients"] >= 0 for p in result["forecast"])
    assert set(result["kpis"]) == {"peak", "peak_date", "average"}
    assert len(result["history"]) > 0


def test_detect_fraud_sorted_and_bounded():
    result = engine.detect_fraud(top=50)
    assert result["total"] >= 0
    assert len(result["suspects"]) <= 50
    scores = [s["score"] for s in result["suspects"]]
    assert scores == sorted(scores)  # plus anormal (score le plus bas) en tête
    if result["suspects"]:
        s = result["suspects"][0]
        assert set(s) == {
            "patient", "visites", "medecins_distincts",
            "hopitaux_distincts", "medicaments_distincts", "score",
        }
```

- [ ] **Step 2: Lancer les tests (doivent échouer)**

Run: `cd backend && source venv/bin/activate && pytest tests/test_ai.py -k "affluence_shape or fraud_sorted" -v`
Expected: FAIL avec `ModuleNotFoundError: No module named 'app.ai.engine'`

- [ ] **Step 3: Implémenter le moteur**

Créer `backend/app/ai/engine.py` :
```python
"""Chargement des modèles IA et inférence (mise en cache mémoire)."""
from functools import lru_cache
from pathlib import Path

import joblib
import numpy as np
import pandas as pd

_AI_DIR = Path(__file__).parent
_MODELS = _AI_DIR / "models"
_DATA = _AI_DIR / "data"

AFFLUENCE_FEATURES = [
    "DayOfWeek", "Month", "Day", "Is_Weekend", "Season",
    "MA7", "Lag_1", "Lag_3", "Lag_7",
]
FRAUD_FEATURES = [
    "Patient_Count", "Unique_Doctors", "Unique_Hospitals", "Unique_Medications",
]


def _season(month: int) -> int:
    if month in (12, 1, 2):
        return 0
    if month in (3, 4, 5):
        return 1
    if month in (6, 7, 8):
        return 2
    return 3


def _anonymize(name: str) -> str:
    parts = str(name).strip().title().split()
    if len(parts) >= 2:
        return f"{parts[0]} {parts[-1][0]}."
    return parts[0] if parts else "—"


@lru_cache(maxsize=1)
def _load():
    affluence_model = joblib.load(_MODELS / "affluence_neural_network.pkl")
    affluence_scaler = joblib.load(_MODELS / "affluence_scaler.pkl")
    fraud_model = joblib.load(_MODELS / "fraud_isolation_forest.pkl")
    fraud_scaler = joblib.load(_MODELS / "fraud_scaler.pkl")
    history = pd.read_csv(_DATA / "affluence_history.csv", parse_dates=["Date"])
    fraud_features = pd.read_csv(_DATA / "fraud_features.csv")
    return (
        affluence_model, affluence_scaler,
        fraud_model, fraud_scaler,
        history, fraud_features,
    )


@lru_cache(maxsize=1)
def predict_affluence(horizon: int = 30) -> dict:
    model, scaler, _, _, history, _ = _load()
    history = history.sort_values("Date")
    counts = history["Patient_Count"]
    last_date = history["Date"].max()

    ma7 = float(counts.tail(7).mean())
    lag1 = float(counts.tail(1).mean())
    lag3 = float(counts.tail(3).mean())
    lag7 = float(counts.tail(7).mean())

    rows = []
    for i in range(1, horizon + 1):
        d = last_date + pd.Timedelta(days=i)
        rows.append({
            "DayOfWeek": d.dayofweek,
            "Month": d.month,
            "Day": d.day,
            "Is_Weekend": 1 if d.dayofweek >= 5 else 0,
            "Season": _season(d.month),
            "MA7": ma7, "Lag_1": lag1, "Lag_3": lag3, "Lag_7": lag7,
            "date": d.strftime("%Y-%m-%d"),
        })
    fut = pd.DataFrame(rows)
    scaled = scaler.transform(fut[AFFLUENCE_FEATURES])
    preds = np.clip(model.predict(scaled), 0, None).round().astype(int)

    forecast = [
        {"date": r["date"], "predicted_patients": int(p)}
        for r, p in zip(rows, preds)
    ]
    hist = [
        {"date": d.strftime("%Y-%m-%d"), "patients": int(c)}
        for d, c in zip(history["Date"], counts)
    ]
    peak_idx = int(preds.argmax())
    kpis = {
        "peak": int(preds.max()),
        "peak_date": forecast[peak_idx]["date"],
        "average": int(round(float(preds.mean()))),
    }
    return {"history": hist, "forecast": forecast, "kpis": kpis}


@lru_cache(maxsize=1)
def detect_fraud(top: int = 50) -> dict:
    _, _, model, scaler, _, features = _load()
    scaled = scaler.transform(features[FRAUD_FEATURES].fillna(0))
    pred = model.predict(scaled)
    scores = model.decision_function(scaled)

    df = features.copy()
    df["is_anomaly"] = pred == -1
    df["score"] = scores
    suspects_df = df[df["is_anomaly"]].sort_values("score").head(top)

    suspects = [
        {
            "patient": _anonymize(row["Name"]),
            "visites": int(row["Patient_Count"]),
            "medecins_distincts": int(row["Unique_Doctors"]),
            "hopitaux_distincts": int(row["Unique_Hospitals"]),
            "medicaments_distincts": int(row["Unique_Medications"]),
            "score": round(float(row["score"]), 3),
        }
        for _, row in suspects_df.iterrows()
    ]
    return {"total": int(df["is_anomaly"].sum()), "suspects": suspects}
```

- [ ] **Step 4: Lancer les tests (doivent passer)**

Run: `cd backend && source venv/bin/activate && pytest tests/test_ai.py -k "affluence_shape or fraud_sorted" -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add backend/app/ai/engine.py backend/tests/test_ai.py
git commit -m "feat(ai): moteur d'inférence affluence et fraude avec cache mémoire"
```

---

### Task 4: Endpoints FastAPI (`router.py`) + enregistrement

**Files:**
- Create: `backend/app/ai/router.py`
- Modify: `backend/app/main.py`
- Modify: `backend/tests/test_ai.py`

**Interfaces:**
- Consumes: `engine.predict_affluence`, `engine.detect_fraud`, `deps.get_current_user`.
- Produces: `GET /ai/affluence` et `GET /ai/fraud` (JSON identiques aux dicts du moteur), protégés par JWT ; `ai.router` importable.

- [ ] **Step 1: Écrire les tests des endpoints**

Ajouter à `backend/tests/test_ai.py` :
```python
def test_affluence_endpoint_requires_auth(client):
    res = client.get("/ai/affluence")
    assert res.status_code in (401, 403)


def test_affluence_endpoint_ok(client, doctor_token):
    res = client.get("/ai/affluence", headers={"Authorization": f"Bearer {doctor_token}"})
    assert res.status_code == 200
    body = res.json()
    assert len(body["forecast"]) == 30
    assert "kpis" in body


def test_fraud_endpoint_ok(client, pharmacist_token):
    res = client.get("/ai/fraud", headers={"Authorization": f"Bearer {pharmacist_token}"})
    assert res.status_code == 200
    body = res.json()
    assert "total" in body
    assert isinstance(body["suspects"], list)
```
(Les fixtures `client`, `doctor_token`, `pharmacist_token` existent déjà dans `backend/tests/conftest.py`.)

- [ ] **Step 2: Lancer les tests (doivent échouer)**

Run: `cd backend && source venv/bin/activate && pytest tests/test_ai.py -k "endpoint" -v`
Expected: FAIL (404 sur `/ai/affluence` car le router n'est pas encore branché).

- [ ] **Step 3: Implémenter le router**

Créer `backend/app/ai/router.py` :
```python
from fastapi import APIRouter, Depends

from ..deps import get_current_user
from ..models import User
from . import engine

router = APIRouter(prefix="/ai", tags=["ai"])


@router.get("/affluence")
def affluence(_: User = Depends(get_current_user)):
    """Prévision d'affluence hospitalière sur 30 jours (dataset de démonstration)."""
    return engine.predict_affluence()


@router.get("/fraud")
def fraud(_: User = Depends(get_current_user)):
    """Patients au comportement atypique (nomadisme médical) — dataset de démo."""
    return engine.detect_fraud()
```

- [ ] **Step 4: Brancher le router dans `main.py`**

Dans `backend/app/main.py`, modifier l'import ligne 3 et ajouter l'enregistrement.

Remplacer :
```python
from .routers import auth, patients, prescriptions, cards
```
par :
```python
from .routers import auth, patients, prescriptions, cards
from .ai import router as ai
```

Et après `app.include_router(cards.router)` ajouter :
```python
app.include_router(ai.router)
```

- [ ] **Step 5: Lancer les tests (doivent passer)**

Run: `cd backend && source venv/bin/activate && pytest tests/test_ai.py -v`
Expected: PASS (tous les tests de `test_ai.py`).

- [ ] **Step 6: Vérifier la non-régression de la suite complète**

Run: `cd backend && source venv/bin/activate && pytest -q`
Expected: tous les tests passent (aucune régression sur auth/patients/prescriptions/cards).

- [ ] **Step 7: Commit**

```bash
git add backend/app/ai/router.py backend/app/main.py backend/tests/test_ai.py
git commit -m "feat(ai): endpoints /ai/affluence et /ai/fraud protégés par JWT"
```

---

### Task 5: Client API frontend + types + dépendance Recharts

**Files:**
- Modify: `web/package.json` (dépendance recharts)
- Modify: `web/src/api/types.ts`
- Modify: `web/src/api/client.ts`

**Interfaces:**
- Produces:
  - Types `AffluencePoint`, `ForecastPoint`, `AffluenceResponse`, `FraudSuspect`, `FraudResponse`.
  - Fonctions `getAffluence()` et `getFraud()` (axios) renvoyant ces types.

- [ ] **Step 1: Installer Recharts**

Run: `cd web && npm install recharts`
Expected: `recharts` ajouté à `dependencies` dans `web/package.json`.

- [ ] **Step 2: Ajouter les types**

Ajouter à la fin de `web/src/api/types.ts` :
```typescript
export interface AffluencePoint {
  date: string;
  patients: number;
}

export interface ForecastPoint {
  date: string;
  predicted_patients: number;
}

export interface AffluenceResponse {
  history: AffluencePoint[];
  forecast: ForecastPoint[];
  kpis: { peak: number; peak_date: string; average: number };
}

export interface FraudSuspect {
  patient: string;
  visites: number;
  medecins_distincts: number;
  hopitaux_distincts: number;
  medicaments_distincts: number;
  score: number;
}

export interface FraudResponse {
  total: number;
  suspects: FraudSuspect[];
}
```

- [ ] **Step 3: Ajouter les appels API**

Dans `web/src/api/client.ts`, ajouter `AffluenceResponse, FraudResponse` à l'import de types (ligne 2), puis ajouter à la fin du fichier :
```typescript
export const getAffluence = () =>
  api.get<AffluenceResponse>("/ai/affluence");

export const getFraud = () =>
  api.get<FraudResponse>("/ai/fraud");
```

- [ ] **Step 4: Vérifier la compilation**

Run: `cd web && npx tsc -b`
Expected: aucune erreur de type.

- [ ] **Step 5: Commit**

```bash
git add web/package.json web/package-lock.json web/src/api/types.ts web/src/api/client.ts
git commit -m "feat(ai): client API affluence/fraude, types et dépendance recharts"
```

---

### Task 6: Page « Analytics IA » + routage accessible aux deux rôles

**Files:**
- Modify: `web/src/components/ProtectedRoute.tsx` (rendre `allowedRole` optionnel)
- Create: `web/src/pages/analytics/AnalyticsPage.tsx`
- Modify: `web/src/App.tsx` (route `/analytics`)
- Modify: `web/src/components/AppShell.tsx` (lien de navigation)

**Interfaces:**
- Consumes: `getAffluence`, `getFraud` (Task 5), `useAuth` (rôle courant), `AppShell`.
- Produces: route `/analytics` accessible à tout utilisateur authentifié, avec graphique d'affluence et tableau de fraude.

- [ ] **Step 1: Rendre `ProtectedRoute` compatible « tout rôle authentifié »**

Remplacer le contenu de `web/src/components/ProtectedRoute.tsx` par :
```typescript
import type { ReactElement } from "react";
import { Navigate } from "react-router-dom";
import { useAuth } from "../hooks/useAuth";

interface Props {
  children: ReactElement;
  allowedRole?: "doctor" | "pharmacist";
}

export default function ProtectedRoute({ children, allowedRole }: Props) {
  const { role } = useAuth();
  if (!role) return <Navigate to="/login" replace />;
  if (allowedRole && role !== allowedRole) return <Navigate to={`/${role}`} replace />;
  return children;
}
```
(Les usages existants avec `allowedRole="doctor"`/`"pharmacist"` restent inchangés.)

- [ ] **Step 2: Créer la page Analytics**

Créer `web/src/pages/analytics/AnalyticsPage.tsx` :
```typescript
import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend,
} from "recharts";
import AppShell from "../../components/AppShell";
import { useAuth } from "../../hooks/useAuth";
import { getAffluence, getFraud } from "../../api/client";
import type { AffluenceResponse, FraudResponse } from "../../api/types";

export default function AnalyticsPage() {
  const { role } = useAuth();
  const navigate = useNavigate();
  const [affluence, setAffluence] = useState<AffluenceResponse | null>(null);
  const [fraud, setFraud] = useState<FraudResponse | null>(null);
  const [error, setError] = useState(false);

  useEffect(() => {
    Promise.all([getAffluence(), getFraud()])
      .then(([a, f]) => {
        setAffluence(a.data);
        setFraud(f.data);
      })
      .catch(() => setError(true));
  }, []);

  // Fusionne historique + prévision pour un seul graphique continu
  const chartData = affluence
    ? [
        ...affluence.history.map((h) => ({ date: h.date, Historique: h.patients })),
        ...affluence.forecast.map((f) => ({ date: f.date, Prévision: f.predicted_patients })),
      ]
    : [];

  return (
    <AppShell role={role ?? "doctor"}>
      <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: 8 }}>
        <h1 style={{ fontSize: 22, fontWeight: 700 }}>🤖 Analytics IA</h1>
        <button className="btn btn-ghost btn-sm" onClick={() => navigate(`/${role}`)}>
          ← Retour
        </button>
      </div>
      <p className="badge badge-info" style={{ marginBottom: 24 }}>
        Données de démonstration
      </p>

      {error && (
        <div className="card" style={{ color: "var(--danger, #c0392b)" }}>
          Module IA indisponible. Vérifiez que le backend tourne sur le port 9000.
        </div>
      )}

      {/* --- Section Affluence --- */}
      <div className="card" style={{ marginBottom: 24 }}>
        <h2 style={{ fontSize: 18, fontWeight: 600, marginBottom: 4 }}>
          Prévision d'affluence (30 jours)
        </h2>
        {affluence && (
          <>
            <div style={{ display: "flex", gap: 24, margin: "12px 0" }}>
              <div><strong style={{ fontSize: 24 }}>{affluence.kpis.peak}</strong><br /><span className="text-muted">Pic prévu ({affluence.kpis.peak_date})</span></div>
              <div><strong style={{ fontSize: 24 }}>{affluence.kpis.average}</strong><br /><span className="text-muted">Moyenne / jour</span></div>
            </div>
            <ResponsiveContainer width="100%" height={280}>
              <LineChart data={chartData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="date" tick={{ fontSize: 11 }} minTickGap={24} />
                <YAxis tick={{ fontSize: 11 }} />
                <Tooltip />
                <Legend />
                <Line type="monotone" dataKey="Historique" stroke="#2563eb" dot={false} strokeWidth={2} />
                <Line type="monotone" dataKey="Prévision" stroke="#f59e0b" dot={false} strokeWidth={2} strokeDasharray="5 5" />
              </LineChart>
            </ResponsiveContainer>
          </>
        )}
      </div>

      {/* --- Section Fraude --- */}
      <div className="card">
        <h2 style={{ fontSize: 18, fontWeight: 600, marginBottom: 4 }}>
          Détection de nomadisme médical
        </h2>
        {fraud && (
          <>
            <p className="text-muted" style={{ marginBottom: 12 }}>
              <strong style={{ color: "var(--danger, #c0392b)" }}>{fraud.total}</strong> patients au comportement atypique — {fraud.suspects.length} plus suspects ci-dessous.
            </p>
            <div style={{ overflowX: "auto" }}>
              <table style={{ width: "100%", borderCollapse: "collapse", fontSize: 14 }}>
                <thead>
                  <tr style={{ textAlign: "left", borderBottom: "1px solid var(--border)" }}>
                    <th style={{ padding: 8 }}>Patient</th>
                    <th style={{ padding: 8 }}>Visites</th>
                    <th style={{ padding: 8 }}>Médecins</th>
                    <th style={{ padding: 8 }}>Hôpitaux</th>
                    <th style={{ padding: 8 }}>Médicaments</th>
                    <th style={{ padding: 8 }}>Score</th>
                  </tr>
                </thead>
                <tbody>
                  {fraud.suspects.map((s, i) => (
                    <tr key={i} style={{ borderBottom: "1px solid var(--border)" }}>
                      <td style={{ padding: 8 }}>{s.patient}</td>
                      <td style={{ padding: 8 }}>{s.visites}</td>
                      <td style={{ padding: 8 }}>{s.medecins_distincts}</td>
                      <td style={{ padding: 8 }}>{s.hopitaux_distincts}</td>
                      <td style={{ padding: 8 }}>{s.medicaments_distincts}</td>
                      <td style={{ padding: 8 }}>
                        <span className="badge" style={{ background: s.score < -0.1 ? "#c0392b" : "#f59e0b", color: "white" }}>
                          {s.score.toFixed(3)}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </>
        )}
      </div>
    </AppShell>
  );
}
```

- [ ] **Step 3: Ajouter la route dans `App.tsx`**

Dans `web/src/App.tsx`, ajouter l'import après les autres pages :
```typescript
import AnalyticsPage from "./pages/analytics/AnalyticsPage";
```
Et ajouter cette route avant la route catch-all `<Route path="*" ...>` :
```typescript
        <Route
          path="/analytics"
          element={
            <ProtectedRoute>
              <AnalyticsPage />
            </ProtectedRoute>
          }
        />
```

- [ ] **Step 4: Ajouter le lien de navigation dans `AppShell`**

Dans `web/src/components/AppShell.tsx`, importer `useNavigate` (déjà importé) et ajouter un bouton « Analytics IA » dans la barre d'en-tête. Dans le `<div className="flex items-center gap-3">` du header, avant le badge de rôle, ajouter :
```typescript
          <button className="btn btn-ghost btn-sm" onClick={() => navigate("/analytics")}>
            🤖 Analytics IA
          </button>
```

- [ ] **Step 5: Vérifier la compilation**

Run: `cd web && npx tsc -b`
Expected: aucune erreur de type.

- [ ] **Step 6: Vérification manuelle end-to-end**

1. Backend : `cd backend && source venv/bin/activate && uvicorn app.main:app --port 9000` (après `python seed.py` si la DB est vide).
2. Web : `cd web && npm run dev` (port 5174).
3. Se connecter (médecin ou pharmacien), cliquer « 🤖 Analytics IA ».
4. Confirmer : la courbe affluence (historique bleu + prévision orange pointillée) est peuplée, le tableau de fraude liste des patients triés par score, le label « Données de démonstration » est visible.

- [ ] **Step 7: Commit**

```bash
git add web/src/components/ProtectedRoute.tsx web/src/pages/analytics/AnalyticsPage.tsx web/src/App.tsx web/src/components/AppShell.tsx
git commit -m "feat(ai): page Analytics IA avec graphique d'affluence et tableau de fraude"
```

---

## Vérification finale

- [ ] `cd backend && source venv/bin/activate && pytest -q` → tout vert.
- [ ] `cd web && npx tsc -b` → aucune erreur.
- [ ] Démo manuelle (Task 6 Step 6) OK.
- [ ] `git status` : le CSV Kaggle de 8 Mo (`_source/`) n'apparaît PAS ; `readmission_risk.pkl` n'est nulle part dans le repo.
- [ ] Mettre à jour la mémoire de projet (axes de différenciation / point de reprise) : partie AI livrée = module Analytics IA (affluence + fraude).
