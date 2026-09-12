"""
train_soil_moisture_model.py
-------------------------------
Trains a RandomForestClassifier on data/soil_moisture_dataset.csv to
predict irrigation_label (LOW / MEDIUM / HIGH) from weather-derived
features. Saves the model + label encoders into modules/ so
soil_moisture_predictor.py can load them.

Features used (all obtainable WITHOUT a physical sensor):
  - temperature_c              (from weather API)
  - humidity_pct                (from weather API)
  - rainfall_mm                 (from weather API, that day's forecast)
  - estimated_soil_moisture_pct (from soil_moisture_estimator.py heuristic)
  - soil_type                   (farmer-selectable, optional, default 'loamy')
  - growth_stage                (farmer-selectable, optional, default 'vegetative')

Run:
  python data/generate_soil_moisture_dataset.py
  python model_training/train_soil_moisture_model.py
"""

import os

import joblib
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder

DATA_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "soil_moisture_dataset.csv")
MODEL_OUT = os.path.join(os.path.dirname(__file__), "..", "modules", "soil_moisture_model.pkl")
ENCODERS_OUT = os.path.join(os.path.dirname(__file__), "..", "modules", "soil_moisture_encoders.pkl")

FEATURE_COLS = [
    "temperature_c", "humidity_pct", "rainfall_mm",
    "estimated_soil_moisture_pct", "soil_enc", "stage_enc",
]


def main():
    df = pd.read_csv(DATA_PATH)

    soil_encoder = LabelEncoder().fit(df["soil_type"])
    stage_encoder = LabelEncoder().fit(df["growth_stage"])

    df["soil_enc"] = soil_encoder.transform(df["soil_type"])
    df["stage_enc"] = stage_encoder.transform(df["growth_stage"])

    X = df[FEATURE_COLS]
    y = df["irrigation_label"]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    model = RandomForestClassifier(
        n_estimators=250,
        max_depth=10,
        min_samples_leaf=4,
        random_state=42,
        class_weight="balanced",
    )
    model.fit(X_train, y_train)

    preds = model.predict(X_test)
    acc = accuracy_score(y_test, preds)
    print(f"Test accuracy: {acc:.4f}")
    print(classification_report(y_test, preds))

    importances = sorted(
        zip(FEATURE_COLS, model.feature_importances_), key=lambda x: -x[1]
    )
    print("Feature importances:")
    for name, imp in importances:
        print(f"  {name}: {imp:.3f}")

    os.makedirs(os.path.dirname(MODEL_OUT), exist_ok=True)
    joblib.dump(model, MODEL_OUT)
    joblib.dump({
        "soil_encoder": soil_encoder,
        "stage_encoder": stage_encoder,
        "feature_cols": FEATURE_COLS,
    }, ENCODERS_OUT)
    print(f"Saved model -> {MODEL_OUT}")
    print(f"Saved encoders -> {ENCODERS_OUT}")


if __name__ == "__main__":
    main()
