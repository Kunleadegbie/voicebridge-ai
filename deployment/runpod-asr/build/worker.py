import base64
import time
from functools import lru_cache

import numpy as np
import runpod
import torch
from transformers import pipeline

from app.services.audio import prepare_audio
from app.services.asr_registry import canonical_language, model_for


@lru_cache(maxsize=4)
def load_model(model_id):
    device = 0 if torch.cuda.is_available() else -1
    dtype = torch.float16 if device == 0 else torch.float32

    return pipeline(
        "automatic-speech-recognition",
        model=model_id,
        device=device,
        torch_dtype=dtype,
    )


def handler(job):
    payload = job.get("input") or {}

    audio_base64 = payload.get("audio_base64")
    language = canonical_language(payload.get("language", "en-NG"))

    if not isinstance(audio_base64, str) or not audio_base64:
        return {"error": "Missing audio_base64"}

    try:
        raw = base64.b64decode(audio_base64, validate=True)

        if len(raw) > 12 * 1024 * 1024:
            return {"error": "Audio exceeds 12 MB limit"}

        prepared = prepare_audio(raw)
        model_id = model_for(language)["model_id"]

        model = load_model(model_id)

        start = time.perf_counter()

        result = model({
            "array": prepared.samples,
            "sampling_rate": prepared.sample_rate,
        })

        transcript = (
            result.get("text", "")
            if isinstance(result, dict)
            else str(result)
        ).strip()

        if not transcript:
            return {"error": "N-ATLAS returned an empty transcription"}

        return {
            "text": transcript,
            "model": model_id,
            "language": language,
            "duration_ms": prepared.duration_ms,
            "asr_latency_ms": int(
                (time.perf_counter() - start) * 1000
            ),
        }

    except Exception as exc:
        return {
            "error": f"ASR processing failed: {type(exc).__name__}"
        }


runpod.serverless.start({"handler": handler})
