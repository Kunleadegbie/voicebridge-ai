import hashlib
import os
import tempfile
import threading
from pathlib import Path

from app.services.spitch_tts import generate_speech
from app.services.speech_usage import reserve_speech_generation


CACHE_DIR = Path(__file__).resolve().parents[2] / "audio_cache"
CACHE_DIR.mkdir(parents=True, exist_ok=True)

_cache_lock = threading.Lock()


def get_or_generate_speech(
    interaction_id: str,
    text: str,
    language: str,
) -> bytes:

    cache_key = hashlib.sha256(
        f"{interaction_id}\0{language}\0{text}".encode("utf-8")
    ).hexdigest()

    cache_path = CACHE_DIR / f"{cache_key}.mp3"

    with _cache_lock:
        if cache_path.is_file():
            cached_audio = cache_path.read_bytes()

            if cached_audio:
                return cached_audio

        # Reserve capacity before making a paid Spitch request.
        reserve_speech_generation()

        audio = generate_speech(
            text=text,
            language=language,
        )

        if not audio:
            raise RuntimeError("Speech provider returned empty audio")

        temp_path = None

        try:
            with tempfile.NamedTemporaryFile(
                mode="wb",
                suffix=".tmp",
                dir=CACHE_DIR,
                delete=False,
            ) as temporary_file:
                temp_path = Path(temporary_file.name)
                temporary_file.write(audio)

            os.replace(temp_path, cache_path)

        finally:
            if temp_path is not None:
                temp_path.unlink(missing_ok=True)

        return audio