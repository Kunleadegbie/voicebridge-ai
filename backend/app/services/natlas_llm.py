from __future__ import annotations

from datetime import datetime
from functools import lru_cache
from typing import Any

import httpx

from app.config import settings
from app.prompts.system import SYSTEM_PROMPT
from app.services.financial_engine import stub_response
from app.services.language import language_name, normalize_language


class NAtlasLLMError(RuntimeError):
    pass


def _messages(text: str, journey: str, language: str) -> list[dict[str, str]]:
    language_code = normalize_language(language)
    response_language = language_name(language_code)

    return [
        {"role": "system", "content": SYSTEM_PROMPT},
        {
            "role": "user",
            "content": (
                f"Required response language: {response_language} ({language_code})\n"
                f"Financial-literacy journey: {journey}\n"
                f"User question: {text}\n\n"
                f"Respond in {response_language}. "
                "Do not switch to English unless Nigerian English is the required "
                "response language or a short English financial/technical term is "
                "necessary for clarity. "
                "If a technical term is retained in English, explain it simply in "
                f"{response_language}. "
                "Give the direct answer first. Use at most three short practical "
                "points. Keep the response suitable for a voice-first interface."
            ),
        },
    ]




async def _generate_api(text: str, journey: str, language: str) -> str:
    import asyncio
    import time

    if not settings.natlas_llm_url:
        raise NAtlasLLMError(
            "NATLAS_LLM_URL is required when NATLAS_LLM_MODE=api."
        )

    if not settings.natlas_llm_api_key:
        raise NAtlasLLMError(
            "NATLAS_LLM_API_KEY is required for Runpod Serverless."
        )

    # Accept a Runpod endpoint base URL or its /run URL.
    base_url = settings.natlas_llm_url.rstrip("/")
    if base_url.endswith("/run"):
        base_url = base_url[:-4]

    if not base_url.startswith("https://api.runpod.ai/v2/"):
        raise NAtlasLLMError(
            "NATLAS_LLM_URL must be a Runpod Serverless endpoint URL."
        )

    request_started = time.monotonic()
    previous_status = None

    messages = _messages(text, journey, language)

    # Runpod vLLM endpoint uses a completion-style prompt.
    # Preserve the system and user instructions.
    prompt = (
        f"System instructions:\n{messages[0]['content']}\n\n"
        f"User request:\n{messages[1]['content']}\n\n"
        "Assistant response:\n"
    )

    payload = {
        "input": {
            "prompt": prompt,
            "sampling_params": {
                "max_tokens": settings.natlas_max_new_tokens,
                "temperature": settings.natlas_temperature,
            },
        }
    }

    headers = {
        "Authorization": f"Bearer {settings.natlas_llm_api_key}",
        "Content-Type": "application/json",
    }

    # Allow sufficient time for Runpod cold starts and queued jobs.
    deadline = time.monotonic() + max(
        360,
        settings.natlas_request_timeout_seconds,
    )

    try:
        async with httpx.AsyncClient(
            timeout=httpx.Timeout(60.0, connect=20.0)
        ) as client:

            submission = await client.post(
                f"{base_url}/run",
                headers=headers,
                json=payload,
            )
            submission.raise_for_status()
            job = submission.json()

            job_id = job.get("id")
            if not job_id:
                raise NAtlasLLMError(
                    f"Runpod did not return a job ID: {job}"
                )

            while True:
                status = job.get("status")

                if status != previous_status:
                    elapsed = time.monotonic() - request_started
                    print(
                        f"[N-ATLAS LLM] Runpod status={status} "
                        f"elapsed={elapsed:.1f}s",
                        flush=True,
                    )
                    previous_status = status
                
                if status == "COMPLETED":
                    total_elapsed_ms = round(
                        (time.monotonic() - request_started) * 1000
                    )

                    queue_delay_ms = job.get("delayTime")
                    execution_time_ms = job.get("executionTime")

                    print(
                        "[N-ATLAS PERFORMANCE] "
                        f"total_elapsed_ms={total_elapsed_ms} | "
                        f"runpod_delay_ms={queue_delay_ms} | "
                        f"runpod_execution_ms={execution_time_ms} | "
                        f"max_output_tokens={settings.natlas_max_new_tokens}",
                        flush=True,
                    )


                if status == "COMPLETED":
                    print(
                        "[N-ATLAS LLM] Runpod metrics: "
                        f"delayTime={job.get('delayTime')} ms, "
                        f"executionTime={job.get('executionTime')} ms",
                        flush=True,
                    )

                if status == "COMPLETED":
                    try:
                        output = job["output"]

                        if isinstance(output, list):
                            result = output[0]
                        elif isinstance(output, dict):
                            result = output
                        else:
                            raise TypeError("Unexpected output structure")

                        choices = result["choices"]
                        choice = choices[0]

                        answer = choice.get("text")

                        if answer is None:
                            answer = choice["message"]["content"]

                        answer = answer.strip()

                        if not answer:
                            raise ValueError("Empty model response")

                        return answer

                    except (
                        KeyError,
                        IndexError,
                        TypeError,
                        AttributeError,
                        ValueError,
                    ) as exc:
                        raise NAtlasLLMError(
                            "Runpod completed but returned an invalid "
                            "N-ATLAS response."
                        ) from exc

                if status in {"FAILED", "CANCELLED", "TIMED_OUT"}:
                    raise NAtlasLLMError(
                        f"Runpod N-ATLAS job ended with status: {status}. "
                        f"Details: {job.get('error', 'Not provided')}"
                    )

                if status not in {
                    "IN_QUEUE",
                    "IN_PROGRESS",
                    "RUNNING",
                }:
                    raise NAtlasLLMError(
                        f"Unexpected Runpod job status: {status}"
                    )

                if time.monotonic() >= deadline:
                    raise NAtlasLLMError(
                        "Runpod N-ATLAS request exceeded the "
                        "configured overall wait time."
                    )

                await asyncio.sleep(3)

                response = await client.get(
                    f"{base_url}/status/{job_id}",
                    headers=headers,
                )
                response.raise_for_status()
                job = response.json()

    except (httpx.HTTPError, ValueError) as exc:
        raise NAtlasLLMError(
            f"Runpod N-ATLAS API request failed: {exc}"
        ) from exc


@lru_cache(maxsize=1)
def _load_local_model() -> tuple[Any, Any, Any]:
    try:
        import torch
        from transformers import AutoModelForCausalLM, AutoTokenizer
    except ImportError as exc:
        raise NAtlasLLMError(
            "Local N-ATLAS mode requires the optional local-model packages. "
            "Install backend/requirements-local.txt first."
        ) from exc

    token = settings.natlas_hf_token or None
    device = settings.natlas_local_device.lower()

    if device == "cuda" and not torch.cuda.is_available():
        raise NAtlasLLMError("NATLAS_LOCAL_DEVICE=cuda but CUDA is not available.")

    if settings.natlas_local_dtype == "float16":
        dtype = torch.float16
    elif settings.natlas_local_dtype == "bfloat16":
        dtype = torch.bfloat16
    elif settings.natlas_local_dtype == "float32":
        dtype = torch.float32
    else:
        dtype = torch.float16 if torch.cuda.is_available() else torch.float32

    tokenizer = AutoTokenizer.from_pretrained(settings.natlas_model_name, token=token)
    model = AutoModelForCausalLM.from_pretrained(
        settings.natlas_model_name,
        token=token,
        torch_dtype=dtype,
        device_map="auto" if device == "auto" else device,
        low_cpu_mem_usage=True,
    )
    return tokenizer, model, torch


def _generate_local(text: str, journey: str, language: str) -> str:
    tokenizer, model, torch = _load_local_model()
    messages = _messages(text, journey, language)

    prompt = tokenizer.apply_chat_template(
        messages,
        add_generation_prompt=True,
        tokenize=False,
        date_string=datetime.now().strftime("%d %b %Y"),
    )
    inputs = tokenizer(prompt, return_tensors="pt", add_special_tokens=False)
    model_device = next(model.parameters()).device
    inputs = {k: v.to(model_device) for k, v in inputs.items()}

    with torch.inference_mode():
        output = model.generate(
            **inputs,
            max_new_tokens=settings.natlas_max_new_tokens,
            use_cache=True,
            repetition_penalty=1.12,
            temperature=settings.natlas_temperature,
            do_sample=settings.natlas_temperature > 0,
        )

    generated = output[0][inputs["input_ids"].shape[1]:]
    return tokenizer.decode(generated, skip_special_tokens=True).strip()


async def generate(text: str, journey: str, language: str) -> tuple[str, bool]:
    mode = settings.natlas_llm_mode.lower().strip()

    if mode == "api":
        return await _generate_api(text, journey, language), True

    if mode == "local":
        return _generate_local(text, journey, language), True

    # Deliberate development fallback. This is visibly labelled STUB/TEST ONLY.
    return stub_response(journey, text), False
