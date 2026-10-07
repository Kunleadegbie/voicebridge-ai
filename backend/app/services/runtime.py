from __future__ import annotations

import os
import platform
import shutil
from pathlib import Path

from app.config import settings


def _memory_gb() -> float | None:
    try:
        import psutil
        return round(psutil.virtual_memory().total / (1024 ** 3), 1)
    except Exception:
        return None


def runtime_status() -> dict:
    cuda_available = False
    gpu_name = None
    gpu_memory_gb = None
    torch_installed = False
    transformers_installed = False

    try:
        import torch
        torch_installed = True
        cuda_available = bool(torch.cuda.is_available())
        if cuda_available:
            gpu_name = torch.cuda.get_device_name(0)
            gpu_memory_gb = round(
                torch.cuda.get_device_properties(0).total_memory / (1024 ** 3), 1
            )
    except Exception:
        pass

    try:
        import transformers  # noqa: F401
        transformers_installed = True
    except Exception:
        pass

    # N-ATLAS is 8B BF16 on the official model card. Full precision local loading
    # is demanding; these are readiness hints, not hard guarantees.
    if cuda_available and (gpu_memory_gb or 0) >= 18:
        local_readiness = "likely"
    elif cuda_available and (gpu_memory_gb or 0) >= 12:
        local_readiness = "possible_with_memory_pressure"
    else:
        local_readiness = "not_recommended_for_full_bf16"

    return {
        "llm_mode": settings.natlas_llm_mode,
        "model": settings.natlas_model_name,
        "python": platform.python_version(),
        "platform": platform.platform(),
        "system_memory_gb": _memory_gb(),
        "torch_installed": torch_installed,
        "transformers_installed": transformers_installed,
        "cuda_available": cuda_available,
        "gpu_name": gpu_name,
        "gpu_memory_gb": gpu_memory_gb,
        "local_full_model_readiness": local_readiness,
        "recommended_competition_route": "official_or_hosted_api",
        "hf_token_configured": bool(settings.natlas_hf_token),
        "llm_url_configured": bool(settings.natlas_llm_url),
    }
