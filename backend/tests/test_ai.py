# joblib.load unpickles data; here the .pkl files are trusted local artifacts
# vendored from the team's own projet_medical_ia.zip, not user-supplied input.
import joblib
import pandas as pd
from pathlib import Path

MODELS = Path(__file__).resolve().parent.parent / "app" / "ai" / "models"
DATA = Path(__file__).resolve().parent.parent / "app" / "ai" / "data"


def test_all_models_load():
    for name in [
        "affluence_neural_network.pkl",
        "affluence_scaler.pkl",
        "fraud_isolation_forest.pkl",
        "fraud_scaler.pkl",
    ]:
        model = joblib.load(MODELS / name)
        assert model is not None


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
