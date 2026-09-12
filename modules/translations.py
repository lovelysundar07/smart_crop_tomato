"""
translations.py
----------------
Central place for every user-facing string in English and Tamil.
Add a new key here whenever a new screen/message is created, so the
language toggle on the frontend always has both versions available.
"""

TRANSLATIONS = {
    "en": {
        "app_title": "Smart Agri Advisor",
        "home_tagline": "AI help for healthier crops and smarter water use",
        "nav_home": "Home",
        "nav_disease": "Leaf Disease Detector",
        "nav_soil": "Soil Moisture Advisor",
        "nav_weather": "Weather Alerts",
        "upload_leaf": "Upload a photo of the leaf",
        "analyze_btn": "Analyze Leaf",
        "result_heading": "Result",
        "confidence": "Confidence",
        "advice_heading": "What you should do",
        "listen_advice": "Listen to advice",
        "soil_heading": "Soil Moisture & Irrigation Advisor",
        "soil_desc": "Type your area (city, town or village) and we'll pull live weather data, estimate soil moisture, and give you a 5-day irrigation plan.",
        "crop_label": "Crop",
        "soil_type_label": "Soil type",
        "last_irrigation_label": "Days since last irrigation",
        "growth_stage_label": "Growth stage",
        "check_btn": "Check Irrigation Need",
        "irrigation_result": "Irrigation Recommendation",
        "analyze_area_btn": "Analyze Area",
        "advanced_options": "Advanced options (optional)",
        "current_conditions": "Current Conditions",
        "temperature_label": "Temperature",
        "humidity_label": "Humidity",
        "rainfall_label": "Rainfall",
        "estimated_moisture_label": "Estimated Soil Moisture",
        "estimated_moisture_note": "Estimated from weather data - not a sensor measurement.",
        "five_day_forecast": "5-Day Irrigation Forecast",
        "irrigation_advice_heading": "AI Irrigation Advice",
        "crop_condition_heading": "Crop Condition",
        "sowing_guidance_heading": "Sowing Guidance",
        "sowing_disclaimer": "Weather-based guidance only - not a guaranteed prediction.",
        "day_today": "Today",
        "day_tomorrow": "Tomorrow",
        "day_n": "Day",
        "rf_model_note": "Irrigation levels are produced by a Random Forest model trained on weather-derived features.",
        "location_not_found": "Location not found. Please check the spelling or try a nearby bigger town.",
        "weather_heading": "Hyperlocal Weather Alerts",
        "weather_desc": "Get a 5-day outlook for your exact location, in simple terms.",
        "location_label": "Your location (village/town)",
        "get_weather_btn": "Get Weather Alert",
        "rain_alert": "Rain expected",
        "heat_alert": "High heat warning",
        "frost_alert": "Frost risk",
        "normal_weather": "Normal conditions expected",
        "no_disease_diseases": "Healthy leaf - no disease detected",
        "footer_note": "Built for small and rural farmers - works on low-cost smartphones.",
        "lang_toggle": "தமிழ்",
        "chatbot_title": "Farmer Assistant",
        "chatbot_greeting": "Hello! Ask me anything about tomato farming, irrigation, soil, weather or pests.",
        "chatbot_placeholder": "Type your question...",
        "chatbot_send": "Send",
        "chatbot_lang_btn": "தமிழ்",
        "chatbot_typing": "Typing...",
        "diseases": {
            "Tomato___Early_blight": "Early Blight",
            "Tomato___Late_blight": "Late Blight",
            "Tomato___Leaf_Mold": "Leaf Mold",
            "Tomato___Septoria_leaf_spot": "Septoria Leaf Spot",
            "Tomato___Spider_mites Two-spotted_spider_mite": "Spider Mite Damage",
            "Tomato___Target_Spot": "Target Spot",
            "Tomato___Tomato_Yellow_Leaf_Curl_Virus": "Yellow Leaf Curl Virus",
            "Tomato___Tomato_mosaic_virus": "Mosaic Virus",
            "Tomato___Bacterial_spot": "Bacterial Spot",
            "Tomato___healthy": "Healthy"
        },
        "advice": {
            "Tomato___Early_blight": "Remove and destroy affected lower leaves. Avoid overhead watering. Apply a copper-based fungicide every 7-10 days. Improve air circulation between plants.",
            "Tomato___Late_blight": "Act fast - this spreads quickly in humid weather. Remove infected plants, avoid wetting leaves, and apply a recommended fungicide immediately. Do not compost infected material.",
            "Tomato___Leaf_Mold": "Increase spacing and ventilation, avoid wetting leaves while watering, and use a fungicide labeled for leaf mold.",
            "Tomato___Septoria_leaf_spot": "Remove infected leaves, mulch the soil to stop spores splashing up, and rotate crops next season.",
            "Tomato___Spider_mites Two-spotted_spider_mite": "Spray plants with water to dislodge mites, use neem oil or insecticidal soap, and keep plants well-watered as mites thrive in dry conditions.",
            "Tomato___Target_Spot": "Remove affected leaves, avoid overhead irrigation, and apply a suitable fungicide.",
            "Tomato___Tomato_Yellow_Leaf_Curl_Virus": "Control whiteflies (the carrier insect) with sticky traps or neem oil, remove infected plants, and use virus-resistant tomato varieties next season.",
            "Tomato___Tomato_mosaic_virus": "Remove and destroy infected plants, wash hands and tools after handling them, and avoid tobacco use near plants.",
            "Tomato___Bacterial_spot": "Use copper-based sprays, avoid working with wet plants, and rotate crops to reduce soil-borne bacteria.",
            "Tomato___healthy": "Your plant looks healthy. Keep up regular watering and monitoring."
        }
    },
    "ta": {
        "app_title": "ஸ்மார்ட் அக்ரி அட்வைசர்",
        "home_tagline": "ஆரோக்கியமான பயிர்களுக்கும், சிறந்த நீர் பயன்பாட்டிற்கும் AI உதவி",
        "nav_home": "முகப்பு",
        "nav_disease": "இலை நோய் கண்டறிதல்",
        "nav_soil": "மண் ஈரப்பத ஆலோசகர்",
        "nav_weather": "வானிலை எச்சரிக்கைகள்",
        "upload_leaf": "இலையின் புகைப்படத்தை பதிவேற்றவும்",
        "analyze_btn": "இலையை பகுப்பாய்வு செய்யவும்",
        "result_heading": "முடிவு",
        "confidence": "நம்பகத்தன்மை",
        "advice_heading": "நீங்கள் என்ன செய்ய வேண்டும்",
        "listen_advice": "ஆலோசனையை கேளுங்கள்",
        "soil_heading": "மண் ஈரப்பதம் & நீர்ப்பாசன ஆலோசகர்",
        "soil_desc": "உங்கள் பகுதியை (நகரம்/ஊர்/கிராமம்) உள்ளிடவும் - நேரடி வானிலை தரவு, மதிப்பிடப்பட்ட மண் ஈரப்பதம் மற்றும் 5-நாள் நீர்ப்பாசன திட்டத்தை பெறுவீர்கள்.",
        "crop_label": "பயிர்",
        "soil_type_label": "மண் வகை",
        "last_irrigation_label": "கடைசி நீர்ப்பாசனத்திலிருந்து நாட்கள்",
        "growth_stage_label": "வளர்ச்சி நிலை",
        "check_btn": "நீர்ப்பாசன தேவையை சரிபார்க்கவும்",
        "irrigation_result": "நீர்ப்பாசன பரிந்துரை",
        "analyze_area_btn": "பகுதியை ஆய்வு செய்யவும்",
        "advanced_options": "மேம்பட்ட விருப்பங்கள் (விருப்பமானது)",
        "current_conditions": "தற்போதைய நிலைமைகள்",
        "temperature_label": "வெப்பநிலை",
        "humidity_label": "ஈரப்பதம்",
        "rainfall_label": "மழைப்பொழிவு",
        "estimated_moisture_label": "மதிப்பிடப்பட்ட மண் ஈரப்பதம்",
        "estimated_moisture_note": "வானிலை தரவிலிருந்து மதிப்பிடப்பட்டது - இது சென்சார் அளவீடு அல்ல.",
        "five_day_forecast": "5-நாள் நீர்ப்பாசன முன்னறிவிப்பு",
        "irrigation_advice_heading": "AI நீர்ப்பாசன ஆலோசனை",
        "crop_condition_heading": "பயிர் நிலை",
        "sowing_guidance_heading": "விதைப்பு வழிகாட்டுதல்",
        "sowing_disclaimer": "வானிலை அடிப்படையிலான வழிகாட்டுதல் மட்டுமே - உத்தரவாதமான கணிப்பு அல்ல.",
        "day_today": "இன்று",
        "day_tomorrow": "நாளை",
        "day_n": "நாள்",
        "rf_model_note": "நீர்ப்பாசன நிலைகள் வானிலை தரவின் அடிப்படையில் பயிற்சி பெற்ற Random Forest மாதிரியால் உருவாக்கப்படுகின்றன.",
        "location_not_found": "இடம் கிடைக்கவில்லை. எழுத்துப்பிழையை சரிபார்க்கவும் அல்லது அருகிலுள்ள பெரிய நகரத்தை முயற்சிக்கவும்.",
        "weather_heading": "உள்ளூர் வானிலை எச்சரிக்கைகள்",
        "weather_desc": "உங்கள் இடத்திற்கான 5 நாள் வானிலை முன்னறிவிப்பு.",
        "location_label": "உங்கள் இடம் (கிராமம்/நகரம்)",
        "get_weather_btn": "வானிலை எச்சரிக்கை பெறவும்",
        "rain_alert": "மழை எதிர்பார்க்கப்படுகிறது",
        "heat_alert": "அதிக வெப்ப எச்சரிக்கை",
        "frost_alert": "பனி பாதிப்பு அபாயம்",
        "normal_weather": "இயல்பான வானிலை எதிர்பார்க்கப்படுகிறது",
        "no_disease_diseases": "ஆரோக்கியமான இலை - நோய் எதுவும் இல்லை",
        "footer_note": "சிறு மற்றும் கிராமப்புற விவசாயிகளுக்காக உருவாக்கப்பட்டது - குறைந்த விலை ஸ்மார்ட்போன்களில் வேலை செய்யும்.",
        "lang_toggle": "English",
        "chatbot_title": "விவசாயி உதவியாளர்",
        "chatbot_greeting": "வணக்கம்! தக்காளி விவசாயம், நீர்ப்பாசனம், மண், வானிலை அல்லது பூச்சிகள் பற்றி என்னிடம் கேளுங்கள்.",
        "chatbot_placeholder": "உங்கள் கேள்வியை தட்டச்சு செய்யவும்...",
        "chatbot_send": "அனுப்பு",
        "chatbot_lang_btn": "English",
        "chatbot_typing": "தட்டச்சு செய்கிறது...",
        "diseases": {
            "Tomato___Early_blight": "ஆரம்ப கருகல் நோய்",
            "Tomato___Late_blight": "பிற்பட்ட கருகல் நோய்",
            "Tomato___Leaf_Mold": "இலை பூஞ்சை",
            "Tomato___Septoria_leaf_spot": "செப்டோரியா இலை புள்ளி நோய்",
            "Tomato___Spider_mites Two-spotted_spider_mite": "சிலந்தி பூச்சி பாதிப்பு",
            "Tomato___Target_Spot": "இலக்கு புள்ளி நோய்",
            "Tomato___Tomato_Yellow_Leaf_Curl_Virus": "மஞ்சள் இலை சுருள் வைரஸ்",
            "Tomato___Tomato_mosaic_virus": "மொசைக் வைரஸ்",
            "Tomato___Bacterial_spot": "பாக்டீரியா புள்ளி நோய்",
            "Tomato___healthy": "ஆரோக்கியமானது"
        },
        "advice": {
            "Tomato___Early_blight": "பாதிக்கப்பட்ட கீழ் இலைகளை அகற்றி அழிக்கவும். மேலிருந்து நீர் பாய்ச்சுவதை தவிர்க்கவும். 7-10 நாட்களுக்கு ஒருமுறை காப்பர் அடிப்படையிலான பூஞ்சைக்கொல்லி பயன்படுத்தவும்.",
            "Tomato___Late_blight": "விரைவாக செயல்படவும் - ஈரப்பதமான வானிலையில் இது வேகமாக பரவும். பாதிக்கப்பட்ட செடிகளை அகற்றவும், இலைகளை ஈரமாக்குவதை தவிர்க்கவும், உடனடியாக பூஞ்சைக்கொல்லி பயன்படுத்தவும்.",
            "Tomato___Leaf_Mold": "இடைவெளியையும் காற்றோட்டத்தையும் அதிகரிக்கவும், நீர்ப்பாசனத்தின் போது இலைகளை ஈரமாக்காமல் இருக்கவும்.",
            "Tomato___Septoria_leaf_spot": "பாதிக்கப்பட்ட இலைகளை அகற்றவும், மண்ணை மூடி பூஞ்சை கிருமிகள் தெறிப்பதை தடுக்கவும்.",
            "Tomato___Spider_mites Two-spotted_spider_mite": "செடிகளில் தண்ணீர் தெளிக்கவும், வேப்பெண்ணெய் அல்லது பூச்சிக்கொல்லி சோப்பு பயன்படுத்தவும்.",
            "Tomato___Target_Spot": "பாதிக்கப்பட்ட இலைகளை அகற்றவும், மேலிருந்து நீர்ப்பாசனத்தை தவிர்க்கவும்.",
            "Tomato___Tomato_Yellow_Leaf_Curl_Virus": "வெள்ளை ஈக்களை கட்டுப்படுத்த ஒட்டும் பொறிகள் அல்லது வேப்பெண்ணெய் பயன்படுத்தவும், பாதிக்கப்பட்ட செடிகளை அகற்றவும்.",
            "Tomato___Tomato_mosaic_virus": "பாதிக்கப்பட்ட செடிகளை அகற்றி அழிக்கவும், கையாண்ட பிறகு கைகளையும் கருவிகளையும் கழுவவும்.",
            "Tomato___Bacterial_spot": "காப்பர் அடிப்படையிலான தெளிப்புகளை பயன்படுத்தவும், ஈரமான செடிகளுடன் வேலை செய்வதை தவிர்க்கவும்.",
            "Tomato___healthy": "உங்கள் செடி ஆரோக்கியமாக உள்ளது. வழக்கமான நீர்ப்பாசனத்தையும் கண்காணிப்பையும் தொடரவும்."
        }
    }
}


def get_text(lang, key):
    """Fetch a simple UI string, falling back to English if missing."""
    lang = lang if lang in TRANSLATIONS else "en"
    return TRANSLATIONS[lang].get(key, TRANSLATIONS["en"].get(key, key))


def get_disease_name(lang, disease_key):
    lang = lang if lang in TRANSLATIONS else "en"
    return TRANSLATIONS[lang]["diseases"].get(disease_key, disease_key)


def get_advice(lang, disease_key):
    lang = lang if lang in TRANSLATIONS else "en"
    return TRANSLATIONS[lang]["advice"].get(disease_key, "")
