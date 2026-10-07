from fastapi import APIRouter
from app.config import settings
from app.services.runtime import runtime_status
from app.services.natlas_asr import asr_diagnostics

router = APIRouter()

@router.get("/health")
def health():
    return {"status":"ok","app":settings.app_name,"asr_mode":settings.natlas_asr_mode,"llm_mode":settings.natlas_llm_mode}

@router.get("/providers/status")
def providers_status():
    return {"asr":asr_diagnostics(),"llm":runtime_status()}

@router.get("/asr/diagnostics")
def diagnostics():
    return asr_diagnostics()
