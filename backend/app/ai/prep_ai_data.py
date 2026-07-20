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
