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
