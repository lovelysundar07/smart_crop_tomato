"""
disease_predictor.py
---------------------
Loads the trained CNN (disease_model.h5) and predicts the disease class
for an uploaded leaf image. Falls back to a friendly "model not found"
message if the model hasn't been trained/copied yet, so the rest of the
app (soil moisture, weather) can still be demoed independently.
"""

import json
import os

import numpy as np
from PIL import Image

MODEL_PATH = os.path.join(os.path.dirname(__file__), "disease_model.h5")
CLASS_MAP_PATH = os.path.join(os.path.dirname(__file__), "class_indices.json")
IMG_SIZE = (160, 160)

_model = None
_class_map = None


def _lazy_load():
    """Load the Keras model only once, only when first needed."""
    global _model, _class_map
    if _model is None and os.path.exists(MODEL_PATH):
        import tensorflow as tf  # imported lazily so the app boots fast without TF loaded upfront
        _model = tf.keras.models.load_model(MODEL_PATH)
        with open(CLASS_MAP_PATH) as f:
            _class_map = json.load(f)
    return _model, _class_map


def is_model_ready():
    return os.path.exists(MODEL_PATH) and os.path.exists(CLASS_MAP_PATH)


def predict(image_path):
    """
    Returns dict: {disease_key, confidence} or {"error": "..."} if the
    model isn't trained yet.
    """
    model, class_map = _lazy_load()
    if model is None:
        return {
            "error": "Model not trained yet. Run model_training/train_disease_model.py "
                     "and copy disease_model.h5 + class_indices.json into modules/."
        }

    img = Image.open(image_path).convert("RGB").resize(IMG_SIZE)
    arr = np.array(img) / 255.0
    arr = np.expand_dims(arr, axis=0)

    preds = model.predict(arr, verbose=0)[0]
    top_idx = int(np.argmax(preds))
    disease_key = class_map[str(top_idx)] if str(top_idx) in class_map else class_map[top_idx]
    confidence = float(preds[top_idx]) * 100

    return {"disease_key": disease_key, "confidence": round(confidence, 2)}
