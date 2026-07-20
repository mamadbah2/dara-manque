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
    # joblib.load unpickles data; these .pkl files are trusted local artifacts
    # vendored from the team's own projet_medical_ia.zip, not user-supplied input.
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
