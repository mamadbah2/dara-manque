# joblib.load unpickles data; here the .pkl files are trusted local artifacts
# vendored from the team's own projet_medical_ia.zip, not user-supplied input.
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
