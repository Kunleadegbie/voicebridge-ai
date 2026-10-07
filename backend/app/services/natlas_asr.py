from __future__ import annotations

import asyncio
import time
from dataclasses import dataclass
from functools import lru_cache

import httpx

from app.config import settings
from app.services.asr_registry import canonical_language, model_for, MODEL_REGISTRY
from app.services.audio import prepare_audio, AudioPreprocessError

class ASRNotConfigured(RuntimeError):
    pass

class NAtlasASRError(RuntimeError):
    pass

@dataclass
class ASRResult:
    transcript: str
    provider: str
    model_id: str
    mode: str
    language: str
    duration_ms: int
    asr_latency_ms: int

@lru_cache(maxsize=4)
def _local_pipeline(model_id: str):
    try:
        import torch
        from transformers import pipeline
    except ImportError as exc:
        raise ASRNotConfigured(
            "Local N-ATLAS ASR dependencies are not installed. Run: pip install -r backend/requirements-asr.txt"
        ) from exc

    device = 0 if torch.cuda.is_available() and settings.natlas_asr_device != "cpu" else -1
    dtype = torch.float16 if device == 0 else torch.float32
    try:
        return pipeline(
            "automatic-speech-recognition",
            model=model_id,
            device=device,
            torch_dtype=dtype,
        )
    except Exception as exc:
        raise NAtlasASRError(
            f"Could not load official N-ATLAS ASR model {model_id}. "
            "Confirm Hugging Face login/gated-model access and internet connectivity. "
            f"Original error: {exc}"
        ) from exc


def _transcribe_local_sync(raw: bytes, filename: str, content_type: str, language: str) -> ASRResult:
    lang = canonical_language(language)
    spec = model_for(lang)
    prepared = prepare_audio(raw, filename, content_type)
    pipe = _local_pipeline(spec["model_id"])
    start = time.perf_counter()
    try:
        result = pipe({"array": prepared.samples, "sampling_rate": prepared.sample_rate})
    except Exception as exc:
        raise NAtlasASRError(f"N-ATLAS ASR inference failed: {exc}") from exc
    transcript = (result.get("text") if isinstance(result, dict) else str(result)).strip()
    if not transcript:
        raise NAtlasASRError("N-ATLAS ASR returned an empty transcript.")
    return ASRResult(
        transcript=transcript,
        provider="natlas",
        model_id=spec["model_id"],
        mode="local",
        language=lang,
        duration_ms=prepared.duration_ms,
        asr_latency_ms=int((time.perf_counter() - start) * 1000),
    )

async def _transcribe_api(raw: bytes, filename: str, content_type: str, language: str) -> ASRResult:
    if not settings.natlas_asr_url:
        raise ASRNotConfigured("N-ATLAS ASR API mode is selected but NATLAS_ASR_URL is empty.")
    headers = {}
    if settings.natlas_asr_api_key:
        headers["Authorization"] = f"Bearer {settings.natlas_asr_api_key}"
    lang = canonical_language(language)
    start = time.perf_counter()
    files = {"file": (filename, raw, content_type or "audio/wav")}
    data = {"language": lang}
    async with httpx.AsyncClient(timeout=settings.natlas_asr_timeout_seconds) as client:
        response = await client.post(settings.natlas_asr_url, headers=headers, files=files, data=data)
        response.raise_for_status()
        payload = response.json()
    transcript = (payload.get("text") or payload.get("transcript") or "").strip()
    if not transcript:
        raise NAtlasASRError("N-ATLAS ASR API response did not contain text/transcript.")
    return ASRResult(
        transcript=transcript,
        provider="natlas",
        model_id=payload.get("model") or model_for(lang)["model_id"],
        mode="api",
        language=lang,
        duration_ms=int(payload.get("duration_ms") or 0),
        asr_latency_ms=int((time.perf_counter() - start) * 1000),
    )

async def transcribe(audio: bytes, filename: str, content_type: str, language: str) -> ASRResult:
    mode = settings.natlas_asr_mode.lower().strip()
    if mode == "local":
        return await asyncio.to_thread(_transcribe_local_sync, audio, filename, content_type, language)
    if mode == "api":
        return await _transcribe_api(audio, filename, content_type, language)
    raise ASRNotConfigured(
        "N-ATLAS ASR is not enabled. Set NATLAS_ASR_MODE=local for the official Hugging Face models, "
        "or api when an official hosted service is supplied."
    )


def asr_diagnostics() -> dict:
    torch_installed = transformers_installed = False
    cuda_available = False
    gpu_name = None
    try:
        import torch
        torch_installed = True
        cuda_available = bool(torch.cuda.is_available())
        if cuda_available:
            gpu_name = torch.cuda.get_device_name(0)
    except Exception:
        pass
    try:
        import transformers  # noqa
        transformers_installed = True
    except Exception:
        pass
    return {
        "mode": settings.natlas_asr_mode,
        "device_preference": settings.natlas_asr_device,
        "torch_installed": torch_installed,
        "transformers_installed": transformers_installed,
        "cuda_available": cuda_available,
        "gpu_name": gpu_name,
        "official_models": {k: v["model_id"] for k, v in MODEL_REGISTRY.items()},
        "first_test_model": MODEL_REGISTRY["en-NG"]["model_id"],
        "model_loading": "lazy_and_cached_in_process",
        "api_url_configured": bool(settings.natlas_asr_url),
        "note": "Local mode uses the official NCAIR1 Hugging Face ASR repositories. Competition interpretation of 'official ASR service' remains subject to NAIC/NCAIR confirmation.",
    }
