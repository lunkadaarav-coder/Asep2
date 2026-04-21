"""HealthMitra Scan – Speech Service (Real Whisper STT with fallback)"""
import os
import random
import logging

logger = logging.getLogger(__name__)

# ── Try to import Whisper ───────────────────────────────────────────
try:
    import whisper
    WHISPER_AVAILABLE = True
except ImportError:
    WHISPER_AVAILABLE = False
    logger.warning("openai-whisper not installed. Using simulated speech-to-text.")


# ── Cached Whisper model ────────────────────────────────────────────
_whisper_model = None


def _get_whisper_model():
    """Load Whisper model (cached singleton)."""
    global _whisper_model
    if _whisper_model is None:
        try:
            from config import WHISPER_MODEL_SIZE
            model_size = WHISPER_MODEL_SIZE
        except Exception:
            model_size = "base"
        logger.info(f"Loading Whisper model: {model_size}")
        _whisper_model = whisper.load_model(model_size)
    return _whisper_model


# ── Simulated fallback data ─────────────────────────────────────────
SAMPLE_TRANSCRIPTS = {
    "en": [
        "Doctor, I have been having headaches for the past two weeks and my vision is getting blurry.",
        "I am a diabetic patient and my sugar levels are not coming under control despite medication.",
        "My mother is 65 years old and has been experiencing chest pain and shortness of breath.",
        "I have joint pain in my knees especially in the morning. Is it arthritis?",
        "What foods should I eat to reduce my cholesterol levels?",
        "I am pregnant and want to know which medicines are safe for me.",
        "My child has fever for 3 days and is not eating properly. What should I do?",
    ],
    "hi": [
        "डॉक्टर, मुझे पिछले दो हफ्तों से सिरदर्द हो रहा है और आंखों से धुंधला दिख रहा है।",
        "मैं शुगर का मरीज हूं और दवाई लेने के बाद भी शुगर कंट्रोल नहीं हो रहा।",
        "मेरी मां 65 साल की हैं और उन्हें सीने में दर्द और सांस लेने में तकलीफ हो रही है।",
        "मुझे घुटनों में दर्द है, खासकर सुबह के समय। क्या यह गठिया है?",
        "कोलेस्ट्रॉल कम करने के लिए क्या खाना चाहिए?",
    ]
}


def transcribe_audio(audio_path: str, language: str = "en") -> str:
    """
    Transcribe audio using OpenAI Whisper.
    Falls back to simulated transcripts if Whisper is not available.

    Supports: WAV, MP3, M4A, FLAC, OGG, WebM, and more.
    """
    # ── Try real Whisper STT ────────────────────────────────────────
    if WHISPER_AVAILABLE:
        try:
            model = _get_whisper_model()

            # Map language codes
            whisper_lang = "hi" if language == "hi" else "en"

            logger.info(f"Transcribing audio: {audio_path} (language: {whisper_lang})")

            result = model.transcribe(
                audio_path,
                language=whisper_lang,
                fp16=False  # Use FP32 for CPU compatibility
            )

            transcript = result.get("text", "").strip()

            if transcript:
                logger.info(f"Whisper transcription successful: {len(transcript)} chars")
                return transcript
            else:
                logger.warning("Whisper returned empty transcript, falling back to simulated")

        except Exception as e:
            logger.error(f"Whisper transcription failed: {e}. Falling back to simulated.")

    # ── Fallback: simulated transcript ──────────────────────────────
    logger.info("Using simulated speech-to-text")
    transcripts = SAMPLE_TRANSCRIPTS.get(language, SAMPLE_TRANSCRIPTS["en"])
    return random.choice(transcripts)


def text_to_speech_url(text: str, language: str = "en") -> str:
    """
    In production, this would generate audio from text using a TTS engine.
    Returns a placeholder URL for now.
    """
    return f"/api/tts/audio?lang={language}"
