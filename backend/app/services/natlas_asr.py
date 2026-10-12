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

async def _transcribe_runpod(raw: bytes, filename: str, content_type: str, language: str) -> ASRResult:
    import base64

    if not settings.natlas_asr_url:
        raise ASRNotConfigured("RunPod ASR mode requires NATLAS_ASR_URL.")
    if not settings.natlas_asr_api_key:
        raise ASRNotConfigured("RunPod ASR mode requires NATLAS_ASR_API_KEY.")

    lang = canonical_language(language)
    endpoint = settings.natlas_asr_url.rstrip("/")
    headers = {
        "Authorization": f"Bearer {settings.natlas_asr_api_key}",
        "Content-Type": "application/json",
    }
    request_body = {
        "input": {
            "audio_base64": base64.b64encode(raw).decode("ascii"),
            "language": lang,
        }
    }

    start = time.perf_counter()
    timeout = settings.natlas_asr_timeout_seconds

    async with httpx.AsyncClient(timeout=timeout) as client:
        response = await client.post(
            f"{endpoint}/run",
            headers=headers,
            json=request_body,
        )
        response.raise_for_status()
        job = response.json()

        job_id = job.get("id")
        if not job_id:
            raise NAtlasASRError("RunPod did not return a job ID.")

        deadline = time.monotonic() + timeout

        while time.monotonic() < deadline:
            status_response = await client.get(
                f"{endpoint}/status/{job_id}",
                headers=headers,
            )
            status_response.raise_for_status()
            status = status_response.json()
            state = status.get("status")

            if state == "COMPLETED":
                output = status.get("output") or {}
                if not isinstance(output, dict):
                    raise NAtlasASRError("RunPod returned an invalid ASR output.")

                if output.get("error"):
                    raise NAtlasASRError(
                        f"RunPod ASR worker error: {output['error']}"
                    )

                transcript = (output.get("text") or "").strip()
                if not transcript:
                    raise NAtlasASRError("RunPod returned an empty transcript.")

                return ASRResult(
                    transcript=transcript,
                    provider="natlas",
                    model_id=output.get("model") or model_for(lang)["model_id"],
                    mode="runpod",
                    language=lang,
                    duration_ms=int(output.get("duration_ms") or 0),
                    asr_latency_ms=int((time.perf_counter() - start) * 1000),
                )

            if state in ("FAILED", "CANCELLED", "TIMED_OUT"):
                raise NAtlasASRError(
                    f"RunPod ASR job ended with status {state}."
                )

            await asyncio.sleep(2)

    raise NAtlasASRError(
        "RunPod ASR timed out while waiting for transcription."
    )

async def transcribe(audio: bytes, filename: str, content_type: str, language: str) -> ASRResult:
    mode = settings.natlas_asr_mode.lower().strip()
    if mode == "local":
        return await asyncio.to_thread(_transcribe_local_sync, audio, filename, content_type, language)
    if mode == "api":
        return await _transcribe_api(audio, filename, content_type, language)
    if mode == "runpod":
        return await _transcribe_runpod(audio, filename, content_type, language)
    raise ASRNotConfigured(
        "N-ATLAS ASR is not enabled. Set NATLAS_ASR_MODE=local for the official Hugging Face models, "
        "or api for an existing hosted service, or runpod for RunPod Serverless."
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
