"""
soil_moisture_predictor.py
----------------------------
Wraps the trained RandomForest irrigation-need classifier.

All numeric features (temperature, humidity, rainfall, estimated soil
moisture) come from the live weather API + soil_moisture_estimator.py -
the farmer never has to type these in. soil_type and growth_stage are
optional selects on the frontend with sensible tomato defaults, so the
common case is "just type your location."
"""

import os

import joblib
import pandas as pd

MODEL_PATH = os.path.join(os.path.dirname(__file__), "soil_moisture_model.pkl")
ENCODERS_PATH = os.path.join(os.path.dirname(__file__), "soil_moisture_encoders.pkl")

DEFAULT_SOIL_TYPE = "loamy"
DEFAULT_GROWTH_STAGE = "vegetative"

_model = None
_encoders = None


def _lazy_load():
    global _model, _encoders
    if _model is None and os.path.exists(MODEL_PATH):
        _model = joblib.load(MODEL_PATH)
        _encoders = joblib.load(ENCODERS_PATH)
    return _model, _encoders


def is_model_ready():
    return os.path.exists(MODEL_PATH) and os.path.exists(ENCODERS_PATH)


def predict(temperature_c, humidity_pct, rainfall_mm, estimated_soil_moisture_pct,
            soil_type=DEFAULT_SOIL_TYPE, growth_stage=DEFAULT_GROWTH_STAGE):
    """
    Returns {"irrigation_label": "LOW"|"MEDIUM"|"HIGH", "confidence": float}
    or {"error": "..."} if the model isn't trained yet.
    """
    model, encoders = _lazy_load()
    if model is None:
        return {
            "error": "Irrigation model not trained yet. Run "
                     "data/generate_soil_moisture_dataset.py then "
                     "model_training/train_soil_moisture_model.py."
        }

    soil_enc_map = encoders["soil_encoder"]
    stage_enc_map = encoders["stage_encoder"]

    soil_type = soil_type if soil_type in soil_enc_map.classes_ else DEFAULT_SOIL_TYPE
    growth_stage = growth_stage if growth_stage in stage_enc_map.classes_ else DEFAULT_GROWTH_STAGE

    soil_val = soil_enc_map.transform([soil_type])[0]
    stage_val = stage_enc_map.transform([growth_stage])[0]

    feature_cols = encoders["feature_cols"]
    features = pd.DataFrame(
        [[temperature_c, humidity_pct, rainfall_mm, estimated_soil_moisture_pct, soil_val, stage_val]],
        columns=feature_cols,
    )

    label = model.predict(features)[0]
    proba = model.predict_proba(features)[0]
    confidence = round(float(max(proba)) * 100, 1)

    return {"irrigation_label": label, "confidence": confidence}


def predict_series(days):
    """
    days: list of dicts already enriched with estimated_soil_moisture_pct
    (from soil_moisture_estimator.estimate_series). soil_type/growth_stage
    may be included per-call via kwargs on the caller side; here we accept
    them as optional keys on each day dict, falling back to defaults.

    Returns the same list with 'irrigation_label' and 'confidence' added.
    """
    out = []
    for day in days:
        result = predict(
            temperature_c=day.get("temperature_c", 30.0),
            humidity_pct=day.get("humidity_pct", 55.0),
            rainfall_mm=day.get("rainfall_mm", 0.0),
            estimated_soil_moisture_pct=day.get("estimated_soil_moisture_pct", 50.0),
            soil_type=day.get("soil_type", DEFAULT_SOIL_TYPE),
            growth_stage=day.get("growth_stage", DEFAULT_GROWTH_STAGE),
        )
        enriched = dict(day)
        enriched.update(result)
        out.append(enriched)
    return out
