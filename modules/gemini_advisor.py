"""
gemini_advisor.py
-------------------
Generates farmer-facing disease advice dynamically using the Gemini API,
instead of a fixed/static advice string. This lets the advice be more
natural, detailed, and adaptable (e.g. it can mention severity, timing,
organic vs chemical options) without you having to hand-write text for
every disease.

SETUP
-----
1. Get a free Gemini API key from https://aistudio.google.com/apikey
2. Install the SDK:  pip install google-generativeai
3. Set the environment variable before running the Flask app:
       export GEMINI_API_KEY="your_key_here"       (Mac/Linux)
       set GEMINI_API_KEY=your_key_here             (Windows)
4. If no key is set, or the call fails (no internet, quota, etc.), a
   short generic fallback message is returned so the demo never breaks
   on stage.

MODEL NAME
----------
GEMINI_MODEL defaults to "gemini-2.0-flash" (fast + cheap, good for this
use case). If Google renames/deprecates it later, just change the
constant below or set the GEMINI_MODEL environment variable.
"""

import os

API_KEY = os.environ.get("GEMINI_API_KEY", "")
MODEL_NAME = os.environ.get("GEMINI_MODEL", "gemini-3.6-flash")

_client_configured = False


def _ensure_configured():
    global _client_configured
    if not _client_configured:
        import google.generativeai as genai
        genai.configure(api_key=API_KEY)
        _client_configured = True


def _build_prompt(disease_name, lang, crop="tomato"):
    if lang == "ta":
        return (
            f"நீங்கள் ஒரு விவசாய நிபுணர். ஒரு {crop} செடியில் '{disease_name}' நோய் "
            f"கண்டறியப்பட்டுள்ளது. கிராமப்புற விவசாயிக்கு எளிய தமிழில், 3-4 குறுகிய "
            f"செயல்படக்கூடிய வாக்கியங்களில் மட்டும் என்ன செய்ய வேண்டும் என்று கூறவும். "
            f"தலைப்புகள், பட்டியல் எண்கள், மார்க்டவுன் குறியீடுகள் இல்லாமல் தெளிவான "
            f"உரையாக மட்டும் பதிலளிக்கவும்."
        )
    return (
        f"You are an agricultural extension expert. A {crop} plant has been diagnosed with "
        f"'{disease_name}'. In simple, plain English suitable for a rural farmer with basic "
        f"literacy, give practical advice in 3-4 short actionable sentences: what caused it, "
        f"what to do now, and how to prevent it next season. No headings, no bullet points, "
        f"no markdown - just plain sentences."
    )


def _fallback_message(lang):
    if lang == "ta":
        return ("இணைய இணைப்பு இல்லை அல்லது AI ஆலோசனை தற்போது கிடைக்கவில்லை. "
                "தயவுசெய்து உங்கள் அருகிலுள்ள வேளாண் அலுவலரை அணுகவும்.")
    return ("Live AI advice is unavailable right now (no internet/API key, or a quota "
            "limit was hit). Please consult your local agricultural extension officer.")


def generate_disease_advice(disease_name, lang="en", crop="tomato"):
    """
    Calls Gemini to generate fresh advice text for the given disease name
    and language. Returns a plain string. Falls back to a short generic
    message on any failure so the app keeps working without breaking.
    """
    if not API_KEY:
        return _fallback_message(lang)

    try:
        _ensure_configured()
        import google.generativeai as genai

        model = genai.GenerativeModel(MODEL_NAME)
        prompt = _build_prompt(disease_name, lang, crop)
        response = model.generate_content(prompt)

        text = (response.text or "").strip()
        return text if text else _fallback_message(lang)

    except Exception as e:
        print(f"[gemini_advisor] Gemini call failed: {e}")
        return _fallback_message(lang)


# ---------------------------------------------------------------------------
# Farmer chatbot
# ---------------------------------------------------------------------------
# A general-purpose Q&A assistant for the floating chat widget. Unlike the
# dashboard advice text (which is deterministic/rule-based for reliability -
# see rule_based_advisor.py), free-text farmer questions genuinely need an
# LLM, so this is where Gemini is used live.

CHAT_SYSTEM_EN = (
    "You are a friendly tomato-farming assistant for small and rural farmers in Tamil Nadu, India, "
    "used inside the 'Smart Tomato Crop Advisor' app. Always answer in simple, plain English a "
    "farmer with basic literacy can understand. Keep answers short (2-5 sentences), practical, and "
    "specific to tomato farming, irrigation, soil, weather, pests and disease. No markdown, no "
    "headings, no bullet points - just plain conversational sentences. If a question is outside "
    "farming topics, gently redirect to farming. If you are not confident about something (like a "
    "regional regulation or exact chemical dosage), say so plainly and suggest checking with a local "
    "agricultural extension officer rather than guessing."
)

CHAT_SYSTEM_TA = (
    "நீங்கள் தமிழ்நாட்டில் உள்ள சிறு மற்றும் கிராமப்புற தக்காளி விவசாயிகளுக்கு உதவும் நட்பான "
    "உதவியாளர், இது 'Smart Tomato Crop Advisor' ஆப்பிற்குள் பயன்படுத்தப்படுகிறது. எப்போதும் எளிய "
    "தமிழில், அடிப்படை படிப்பறிவு உள்ள விவசாயி புரிந்துகொள்ளும் வகையில் பதிலளிக்கவும். பதில்களை "
    "குறுகியதாக (2-5 வாக்கியங்கள்), நடைமுறைக்கு உகந்ததாக, தக்காளி விவசாயம், நீர்ப்பாசனம், மண், "
    "வானிலை, பூச்சி மற்றும் நோய் தொடர்பானதாக மட்டும் வைத்திருக்கவும். மார்க்டவுன், தலைப்புகள், "
    "பட்டியல்கள் இல்லாமல் எளிய பேச்சு வாக்கியங்களாக மட்டும் பதிலளிக்கவும். கேள்வி விவசாயத்திற்கு "
    "வெளியே இருந்தால், மெதுவாக விவசாயத்திற்கு திருப்பிவிடவும். ஏதேனும் ஒரு விஷயத்தில் (பிராந்திய "
    "விதிமுறைகள் அல்லது துல்லியமான மருந்தளவு போன்றவை) உறுதியாக தெரியவில்லை என்றால், அதை தெளிவாக "
    "கூறி, யூகிக்காமல் உள்ளூர் வேளாண் அலுவலரை அணுகுமாறு பரிந்துரைக்கவும்."
)


def _chat_fallback(lang):
    if lang == "ta":
        return ("மன்னிக்கவும், இந்த நேரத்தில் AI உதவியாளருடன் இணைக்க முடியவில்லை (இணைய இணைப்பு "
                "இல்லை அல்லது API வரம்பு எட்டப்பட்டது). உங்கள் அருகிலுள்ள வேளாண் அலுவலரை "
                "அணுகவும் அல்லது சிறிது நேரம் கழித்து மீண்டும் முயற்சிக்கவும்.")
    return ("Sorry, I can't reach the AI assistant right now (no internet, no API key set, or a "
            "quota limit was hit). Please try again shortly, or consult your local agricultural "
            "extension officer.")


def chat_reply(message, lang="en", history=None):
    """
    Generates a chatbot reply for a farmer's free-text question.
    `history` is an optional list of {"role": "user"|"model", "text": "..."}
    from earlier turns in the same conversation, most recent last.
    Falls back to a short apology message on any failure (no key, no
    internet, quota, etc.) so the widget never breaks the rest of the app.
    """
    if not message or not message.strip():
        return _chat_fallback(lang)

    if not API_KEY:
        return _chat_fallback(lang)

    try:
        _ensure_configured()
        import google.generativeai as genai

        system_prompt = CHAT_SYSTEM_TA if lang == "ta" else CHAT_SYSTEM_EN
        model = genai.GenerativeModel(MODEL_NAME, system_instruction=system_prompt)

        convo = []
        for turn in (history or [])[-6:]:
            role = "model" if turn.get("role") == "model" else "user"
            convo.append({"role": role, "parts": [turn.get("text", "")]})

        chat = model.start_chat(history=convo)
        response = chat.send_message(message.strip())

        text = (response.text or "").strip()
        return text if text else _chat_fallback(lang)

    except Exception as e:
        print(f"[gemini_advisor] Chatbot call failed: {e}")
        return _chat_fallback(lang)
