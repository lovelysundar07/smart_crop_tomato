"""
voice_advisor.py
------------------
Converts advisory text into speech (Tamil or English) using gTTS
(Google Text-to-Speech). This is the "voice-first" piece: instead of
forcing a farmer to read the advice, they can press a Listen button.

WHY gTTS?
  - Free, no API key required
  - Supports Tamil ('ta') and English ('en') out of the box
  - Needs only an internet connection to generate the audio file
    (generation happens once per result; the .mp3 is then served
    like a normal static file, so playback itself does not need
    internet again for that specific clip)

NOTE ON VOICE INPUT (farmer speaking a question):
  True Tamil speech-to-text needs a heavier model (e.g. Google Cloud
  Speech-to-Text, or an on-device Vosk Tamil model). For the hackathon
  MVP we recommend starting with TEXT input + VOICE output (this file),
  and adding voice input as a stretch goal using the browser's built-in
  Web Speech API (works for English reliably; Tamil support varies by
  browser/OS, mention this as a "future work" slide point).
"""

import hashlib
import os

AUDIO_DIR = os.path.join(os.path.dirname(__file__), "..", "static", "audio")
os.makedirs(AUDIO_DIR, exist_ok=True)


def text_to_speech(text, lang="en"):
    """
    Generates (or reuses a cached) mp3 for the given text+language and
    returns the relative static path the frontend can play directly.
    gTTS is imported lazily (only when this function actually runs) so
    the whole app still boots even before `pip install gtts` / without
    an internet connection - the rest of the demo (disease + soil +
    weather) keeps working, just without audio playback.
    """
    lang_code = "ta" if lang == "ta" else "en"

    file_hash = hashlib.md5(f"{lang_code}:{text}".encode("utf-8")).hexdigest()[:16]
    filename = f"advice_{lang_code}_{file_hash}.mp3"
    filepath = os.path.join(AUDIO_DIR, filename)

    if not os.path.exists(filepath):
        try:
            from gtts import gTTS
            tts = gTTS(text=text, lang=lang_code)
            tts.save(filepath)
        except Exception as e:
            # No internet / gTTS not installed - fail gracefully, no audio this time
            print(f"[voice_advisor] Could not generate audio: {e}")
            return None

    return f"/static/audio/{filename}"
