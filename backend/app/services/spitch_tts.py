import os
from pathlib import Path

from spitch import Spitch


VOICE_SETTINGS = {
    "en-NG": {"language": "en", "voice": "kani"},
    "yo-NG": {"language": "yo", "voice": "femi"},
    "ig-NG": {"language": "ig", "voice": "ngozi"},
    "ha-NG": {"language": "ha", "voice": "zainab"},
}


def load_spitch_key():
    """Load the API key without displaying it."""

    if os.getenv("SPITCH_API_KEY"):
        return

    env_path = Path(__file__).resolve().parents[3] / ".env"

    if not env_path.exists():
        raise RuntimeError("VoiceBridge .env file not found")

    for line in env_path.read_text(
        encoding="utf-8-sig"
    ).splitlines():

        if line.strip().startswith("SPITCH_API_KEY="):
            key = line.split("=", 1)[1].strip().strip('"').strip("'")

            if key:
                os.environ["SPITCH_API_KEY"] = key
                return

    raise RuntimeError("SPITCH_API_KEY is not configured")


def generate_speech(text: str, language: str) -> bytes:
    """Generate an MP3 spoken answer using Spitch."""

    if language not in VOICE_SETTINGS:
        raise ValueError(f"TTS language not configured: {language}")

    if not text or not text.strip():
        raise ValueError("Cannot generate speech from empty text")

    if len(text) > 2000:
        raise ValueError("Text exceeds the TTS safety limit")

    load_spitch_key()

    settings = VOICE_SETTINGS[language]

    client = Spitch()

    response = client.speech.generate(
        text=text,
        language=settings["language"],
        voice=settings["voice"],
        speed=1.0,
        format="mp3",
    )

    return response.read()