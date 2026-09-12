"""
rule_based_advisor.py
------------------------
Generates the farmer-facing explanation text on the Soil & Irrigation
dashboard: irrigation advice, weather situation summary, crop
maintenance tips, and sowing guidance.

WHY RULE-BASED INSTEAD OF LIVE GEMINI HERE?
On a hackathon demo you cannot rely on conference wifi or API quota for
your CORE dashboard numbers - and free-text LLM generation of specific
agronomic claims ("irrigate now") risks being subtly wrong/hallucinated
each time. So this text is deterministic, bilingual (EN/TA), fast, and
reproducible - it always reflects exactly the numbers computed by the
weather API + soil moisture estimator + Random Forest. Gemini is used
separately for the open-ended chatbot, where free-text Q&A is the
actual use case it's good at.

All functions take the already-enriched 5-day list (from
soil_moisture_estimator + soil_moisture_predictor) and return plain,
farmer-friendly strings.
"""

def _t(lang, en, ta):
    return ta if lang == "ta" else en


def irrigation_advice(days, lang="en"):
    today = days[0]
    rain_next2 = sum(d.get("rainfall_mm", 0) for d in days[1:3])
    moisture_trend = days[-1]["estimated_soil_moisture_pct"] - days[0]["estimated_soil_moisture_pct"]
    label_today = today.get("irrigation_label", "MEDIUM")

    if rain_next2 >= 10:
        if label_today == "HIGH":
            return _t(lang,
                f"Estimated soil moisture is currently low, but {round(rain_next2)}mm of rain is expected "
                f"in the next two days. You may still need a light irrigation today to avoid stress, "
                f"then rely on the rain and skip irrigation for the following couple of days.",
                f"தற்போது மதிப்பிடப்பட்ட மண் ஈரப்பதம் குறைவாக உள்ளது, ஆனால் அடுத்த இரண்டு நாட்களில் "
                f"சுமார் {round(rain_next2)}மிமீ மழை எதிர்பார்க்கப்படுகிறது. இன்று ஒரு லேசான நீர்ப்பாசனம் "
                f"தேவைப்படலாம், அதன் பிறகு மழையை நம்பி சில நாட்கள் நீர்ப்பாசனத்தை தவிர்க்கலாம்.")
        return _t(lang,
            f"Rainfall of about {round(rain_next2)}mm is expected over the next two days, so irrigation "
            f"can likely be reduced or skipped for now.",
            f"அடுத்த இரண்டு நாட்களில் சுமார் {round(rain_next2)}மிமீ மழை எதிர்பார்க்கப்படுகிறது, எனவே "
            f"தற்போது நீர்ப்பாசனத்தை குறைக்கலாம் அல்லது தவிர்க்கலாம்.")

    if label_today == "HIGH" or moisture_trend < -8:
        return _t(lang,
            "Low rainfall is expected and estimated soil moisture is falling, so irrigation is "
            "recommended today. Check the top few centimetres of soil by hand before watering.",
            "குறைந்த மழை எதிர்பார்க்கப்படுகிறது மற்றும் மதிப்பிடப்பட்ட மண் ஈரப்பதம் குறைந்து வருகிறது, "
            "எனவே இன்று நீர்ப்பாசனம் பரிந்துரைக்கப்படுகிறது. நீர்ப்பாசனத்திற்கு முன் மண்ணின் மேல் "
            "பகுதியை கையால் சரிபார்க்கவும்.")

    if label_today == "LOW":
        return _t(lang,
            "Estimated soil moisture looks adequate for now. Irrigation does not appear urgent - "
            "recheck in a day or two.",
            "தற்போது மதிப்பிடப்பட்ட மண் ஈரப்பதம் போதுமானதாக தெரிகிறது. நீர்ப்பாசனம் அவசரமாக "
            "தேவையில்லை - ஒன்று அல்லது இரண்டு நாட்களில் மீண்டும் சரிபார்க்கவும்.")

    return _t(lang,
        "Conditions are moderate. A light to medium irrigation in the next day or two should be "
        "enough - watch the rainfall forecast before deciding.",
        "நிலைமைகள் மிதமானவை. அடுத்த ஒன்று அல்லது இரண்டு நாட்களில் லேசான முதல் நடுத்தர "
        "நீர்ப்பாசனம் போதுமானதாக இருக்கும் - முடிவெடுக்கும் முன் மழை முன்னறிவிப்பை கவனிக்கவும்.")


def weather_situation(days, lang="en"):
    today = days[0]
    avg_humidity = sum(d["humidity_pct"] for d in days) / len(days)
    max_temp = max(d["temperature_c"] for d in days)
    total_rain = sum(d["rainfall_mm"] for d in days)

    parts = []
    if total_rain >= 15:
        parts.append(_t(lang, "rainfall is expected over the coming days",
                               "வரும் நாட்களில் மழை எதிர்பார்க்கப்படுகிறது"))
    elif total_rain <= 2:
        parts.append(_t(lang, "the area looks dry with little rain expected",
                               "இப்பகுதி வறண்டதாக உள்ளது, மழை மிகக் குறைவாக எதிர்பார்க்கப்படுகிறது"))
    else:
        parts.append(_t(lang, "only light rainfall is expected",
                               "லேசான மழை மட்டும் எதிர்பார்க்கப்படுகிறது"))

    if avg_humidity >= 80:
        parts.append(_t(lang, "humidity is quite high, which raises disease risk on leaves",
                               "ஈரப்பதம் மிக அதிகமாக உள்ளது, இது இலைகளில் நோய் ஏற்படும் அபாயத்தை அதிகரிக்கிறது"))
    elif avg_humidity <= 40:
        parts.append(_t(lang, "humidity is low, which can stress the plants",
                               "ஈரப்பதம் குறைவாக உள்ளது, இது செடிகளுக்கு அழுத்தத்தை ஏற்படுத்தும்"))

    if max_temp >= 38:
        parts.append(_t(lang, "temperatures are expected to get quite high, which is stressful for tomatoes",
                               "வெப்பநிலை மிக அதிகமாக இருக்கும் என எதிர்பார்க்கப்படுகிறது, இது தக்காளிக்கு அழுத்தமானது"))
    elif max_temp <= 15:
        parts.append(_t(lang, "temperatures are on the cooler side for tomatoes",
                               "வெப்பநிலை தக்காளிக்கு குளிர்ச்சியான பக்கத்தில் உள்ளது"))

    joined = "; ".join(parts) + "."
    intro = _t(lang, "Over the next few days, ", "அடுத்த சில நாட்களில், ")
    return intro + joined[0].upper() + joined[1:] if joined else intro


def crop_maintenance_advice(days, growth_stage="vegetative", lang="en"):
    avg_humidity = sum(d["humidity_pct"] for d in days) / len(days)
    tips_en = []
    tips_ta = []

    if avg_humidity >= 75:
        tips_en.append("Watch leaves closely for early signs of fungal disease since humidity is high.")
        tips_ta.append("ஈரப்பதம் அதிகமாக இருப்பதால் இலைகளில் பூஞ்சை நோய் அறிகுறிகளை கவனமாக கண்காணிக்கவும்.")
        tips_en.append("Improve airflow between plants and avoid wetting leaves when watering.")
        tips_ta.append("செடிகளுக்கு இடையே காற்றோட்டத்தை அதிகரிக்கவும், நீர்ப்பாசனத்தின் போது இலைகளை ஈரமாக்குவதை தவிர்க்கவும்.")

    total_rain = sum(d["rainfall_mm"] for d in days)
    if total_rain >= 20:
        tips_en.append("Check drainage - waterlogged soil can damage tomato roots.")
        tips_ta.append("வடிகால் வசதியை சரிபார்க்கவும் - தண்ணீர் தேங்குவது தக்காளி வேர்களை பாதிக்கக்கூடும்.")

    if growth_stage in ("flowering", "fruiting"):
        tips_en.append("Keep watering consistent during flowering/fruiting - irregular watering can cause fruit cracking or flower drop.")
        tips_ta.append("பூக்கும்/காய்க்கும் நேரத்தில் நீர்ப்பாசனத்தை சீராக வைத்திருக்கவும் - முறையற்ற நீர்ப்பாசனம் காய் வெடிப்பு அல்லது பூ உதிர்தலை ஏற்படுத்தலாம்.")

    if not tips_en:
        tips_en.append("Conditions look manageable - continue routine monitoring and watering as needed.")
        tips_ta.append("நிலைமைகள் நிர்வகிக்கக்கூடியதாக உள்ளன - வழக்கமான கண்காணிப்பையும் தேவைக்கேற்ப நீர்ப்பாசனத்தையும் தொடரவும்.")

    return " ".join(tips_ta if lang == "ta" else tips_en)


def sowing_guidance(days, lang="en"):
    """
    IMPORTANT: rule-based weather guidance, not a scientific prediction.
    Sowing timing depends on soil temperature/condition, tomato variety,
    local crop calendar and practices too - not weather alone.
    """
    total_rain = sum(d.get("rainfall_mm", 0) for d in days[:3])
    avg_temp = sum(d["temperature_c"] for d in days[:3]) / 3
    avg_moisture = sum(d["estimated_soil_moisture_pct"] for d in days[:3]) / 3

    ideal_temp = 18 <= avg_temp <= 29

    if total_rain >= 25:
        return _t(lang,
            "Heavy rainfall is expected over the next few days, so immediate sowing may be less "
            "suitable. Consider waiting for a more stable weather window and avoid waterlogged soil. "
            "This is weather-based guidance only - please also confirm soil condition and your local "
            "tomato crop calendar before sowing.",
            "அடுத்த சில நாட்களில் அதிக மழை எதிர்பார்க்கப்படுவதால், உடனடியாக விதைப்பது பொருத்தமாக "
            "இருக்காது. நிலையான வானிலைக்காக காத்திருக்கவும், தண்ணீர் தேங்கிய மண்ணை தவிர்க்கவும். "
            "இது வானிலை அடிப்படையிலான வழிகாட்டுதல் மட்டுமே - விதைப்பதற்கு முன் மண் நிலையையும் "
            "உள்ளூர் பயிர் காலண்டரையும் உறுதி செய்யவும்.")

    if ideal_temp and 30 <= avg_moisture <= 75 and total_rain < 25:
        return _t(lang,
            "Current weather appears moderately favourable for sowing - temperatures are in a "
            "reasonable range and soil moisture is estimated to be adequate. This is weather-based "
            "guidance only; please confirm soil condition, seed variety, and your local crop calendar "
            "before planting.",
            "தற்போதைய வானிலை விதைப்பதற்கு மிதமாக பொருத்தமாக தெரிகிறது - வெப்பநிலை நியாயமான "
            "வரம்பில் உள்ளது, மதிப்பிடப்பட்ட மண் ஈரப்பதமும் போதுமானதாக உள்ளது. இது வானிலை "
            "அடிப்படையிலான வழிகாட்டுதல் மட்டுமே; விதைப்பதற்கு முன் மண் நிலை, விதை வகை, உள்ளூர் "
            "பயிர் காலண்டரை உறுதி செய்யவும்.")

    return _t(lang,
        "Weather conditions are only partially suitable right now - temperature or estimated soil "
        "moisture is outside the ideal range for sowing. It may be worth waiting a few days and "
        "rechecking. This is weather-based guidance only, not a guarantee - confirm soil condition "
        "and your local crop calendar before sowing.",
        "தற்போது வானிலை நிலைமைகள் ஓரளவு மட்டுமே பொருத்தமானவை - வெப்பநிலை அல்லது மதிப்பிடப்பட்ட "
        "மண் ஈரப்பதம் விதைப்பதற்கு ஏற்ற வரம்பிற்கு வெளியே உள்ளது. சில நாட்கள் காத்திருந்து மீண்டும் "
        "சரிபார்ப்பது நல்லது. இது வானிலை அடிப்படையிலான வழிகாட்டுதல் மட்டுமே - உறுதிசெய்ய "
        "மண் நிலையையும் உள்ளூர் பயிர் காலண்டரையும் பார்க்கவும்.")
