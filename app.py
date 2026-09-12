"""
app.py
-------
Main Flask application for the Smart Tomato Crop Advisor hackathon project.

Modules wired together here:
  - modules/disease_predictor.py        -> CNN tomato leaf disease detection
  - modules/soil_moisture_estimator.py  -> "Estimated Soil Moisture" heuristic (weather-derived, not a sensor)
  - modules/soil_moisture_predictor.py  -> Random Forest irrigation advisor
  - modules/rule_based_advisor.py       -> bilingual irrigation/weather/maintenance/sowing text
  - modules/weather_api.py              -> hyperlocal weather + 5-day forecast
  - modules/gemini_advisor.py           -> disease advice text + farmer chatbot (Gemini)
  - modules/voice_advisor.py            -> Tamil/English text-to-speech
  - modules/translations.py             -> EN/TA UI strings

Run with:  python app.py
Then open: http://127.0.0.1:5000
"""
from dotenv import load_dotenv
load_dotenv()
import os
import uuid

from flask import Flask, jsonify, render_template, request, session

from modules import (
    disease_predictor,
    gemini_advisor,
    rule_based_advisor,
    soil_moisture_estimator,
    soil_moisture_predictor,
    voice_advisor,
    weather_api,
)
from modules.translations import TRANSLATIONS, get_disease_name, get_text

app = Flask(__name__)
app.secret_key = "change-this-secret-key-for-production"

UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), "uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER


def current_lang():
    return session.get("lang", "en")


@app.context_processor
def inject_translation_helper():
    """Makes t('key') available directly inside every Jinja template."""
    lang = current_lang()
    return {"t": lambda key: get_text(lang, key), "current_lang": lang}


@app.route("/set-language/<lang_code>")
def set_language(lang_code):
    if lang_code in TRANSLATIONS:
        session["lang"] = lang_code
    return jsonify({"status": "ok", "lang": current_lang()})


@app.route("/")
def home():
    return render_template("index.html")


# ---------------------------------------------------------------------------
# Disease detection (unchanged from the existing project)
# ---------------------------------------------------------------------------

@app.route("/disease-detector")
def disease_detector_page():
    return render_template("disease_detector.html", model_ready=disease_predictor.is_model_ready())


@app.route("/api/detect-disease", methods=["POST"])
def api_detect_disease():
    lang = current_lang()
    if "leaf_image" not in request.files:
        return jsonify({"error": "No image uploaded"}), 400

    file = request.files["leaf_image"]
    filename = f"{uuid.uuid4().hex}_{file.filename}"
    filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
    file.save(filepath)

    result = disease_predictor.predict(filepath)
    if "error" in result:
        return jsonify(result), 503

    disease_key = result["disease_key"]
    disease_name = get_disease_name(lang, disease_key)

    # advice comes live from Gemini instead of a fixed/static string
    advice_text = gemini_advisor.generate_disease_advice(disease_name, lang=lang, crop="tomato")

    audio_path = voice_advisor.text_to_speech(advice_text, lang=lang)

    return jsonify({
        "disease_key": disease_key,
        "disease_name": disease_name,
        "confidence": result["confidence"],
        "advice": advice_text,
        "audio_url": audio_path,
        "is_healthy": disease_key.endswith("healthy"),
    })


# ---------------------------------------------------------------------------
# Soil Moisture & Irrigation — location-first dashboard, Random Forest based
# ---------------------------------------------------------------------------

@app.route("/soil-moisture")
def soil_moisture_page():
    return render_template("soil_moisture.html", model_ready=soil_moisture_predictor.is_model_ready())


@app.route("/api/soil-moisture", methods=["POST"])
def api_soil_moisture():
    lang = current_lang()
    data = request.get_json(silent=True) or {}

    location = (data.get("location") or "").strip()
    soil_type = (data.get("soil_type") or "loamy").strip().lower()
    growth_stage = (data.get("growth_stage") or "vegetative").strip().lower()

    if not location:
        return jsonify({"error": get_text(lang, "location_label")}), 400

    forecast = weather_api.get_forecast(location)
    if "error" in forecast or not forecast.get("days"):
        return jsonify({"error": get_text(lang, "location_not_found")}), 404

    if not soil_moisture_predictor.is_model_ready():
        return jsonify({
            "error": "Irrigation model not trained yet. Run "
                     "data/generate_soil_moisture_dataset.py then "
                     "model_training/train_soil_moisture_model.py."
        }), 503

    # 1. Estimate soil moisture across the 5-day window - a weather-derived
    #    heuristic, NOT a sensor measurement (see soil_moisture_estimator.py)
    enriched_days = soil_moisture_estimator.estimate_series(forecast["days"])
    for day in enriched_days:
        day["soil_type"] = soil_type
        day["growth_stage"] = growth_stage

    # 2. Random Forest irrigation recommendation per day
    forecast_with_rf = soil_moisture_predictor.predict_series(enriched_days)

    # 3. Bilingual, rule-based farmer-facing explanations (kept deterministic
    #    for demo reliability - see rule_based_advisor.py docstring)
    irrigation_advice = rule_based_advisor.irrigation_advice(forecast_with_rf, lang=lang)
    weather_situation = rule_based_advisor.weather_situation(forecast_with_rf, lang=lang)
    crop_maintenance = rule_based_advisor.crop_maintenance_advice(forecast_with_rf, growth_stage, lang=lang)
    sowing_guidance = rule_based_advisor.sowing_guidance(forecast_with_rf, lang=lang)

    audio_path = voice_advisor.text_to_speech(irrigation_advice, lang=lang)

    return jsonify({
        "location": forecast.get("location", location),
        "source": forecast.get("source", "unknown"),
        "soil_type": soil_type,
        "growth_stage": growth_stage,
        "forecast": forecast_with_rf,
        "irrigation_advice": irrigation_advice,
        "weather_situation": weather_situation,
        "crop_maintenance": crop_maintenance,
        "sowing_guidance": sowing_guidance,
        "model_note": get_text(lang, "rf_model_note"),
        "audio_url": audio_path,
    })


# ---------------------------------------------------------------------------
# Weather alerts (unchanged from the existing project)
# ---------------------------------------------------------------------------

@app.route("/weather-alerts")
def weather_alerts_page():
    return render_template("weather_alert.html")


@app.route("/api/weather-alerts", methods=["POST"])
def api_weather_alerts():
    data = request.get_json(silent=True) or {}
    location = data.get("location", "")
    if not location:
        return jsonify({"error": "Please provide a location"}), 400

    forecast = weather_api.get_forecast(location)
    if "error" in forecast:
        return jsonify(forecast), 404

    alerts = weather_api.build_alerts(forecast)
    return jsonify({"forecast": forecast, "alerts": alerts})


# ---------------------------------------------------------------------------
# Gemini farmer chatbot (new) - floating widget, top-right, on every page
# ---------------------------------------------------------------------------

@app.route("/api/chatbot", methods=["POST"])
def api_chatbot():
    default_lang = current_lang()
    data = request.get_json(silent=True) or {}

    message = (data.get("message") or "").strip()
    lang = data.get("lang", default_lang)
    lang = lang if lang in TRANSLATIONS else default_lang
    history = data.get("history") or []

    if not message:
        return jsonify({"error": "empty_message"}), 400

    reply = gemini_advisor.chat_reply(message, lang=lang, history=history)
    return jsonify({"reply": reply, "lang": lang})


if __name__ == "__main__":
    app.run()
