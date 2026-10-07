import time
from fastapi import APIRouter, UploadFile, File, Form, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.db.models import Interaction
from app.schemas.interaction import VoiceAnswer
from app.schemas.voice import TextTestIn
from app.services.natlas_asr import transcribe, ASRNotConfigured, NAtlasASRError
from app.services.audio import AudioPreprocessError
from app.services.natlas_llm import generate, NAtlasLLMError
from app.services.financial_engine import classify_journey
from app.services.language import normalize_language
from app.services.safety import redact, safety_suffix, precheck
from app.config import settings
router=APIRouter()

def is_validation_eligible(
    source: str,
    natlas_asr: bool,
    real_user: bool,
    completed: bool = True,
) -> bool:
    """
    A VoiceBridge interaction qualifies for real-user validation only when:
    - it is a voice interaction,
    - official N-ATLAS ASR was successfully used,
    - it is explicitly marked as a real-user interaction, and
    - the interaction completed successfully.
    """
    return bool(
        source == "voice"
        and natlas_asr
        and real_user
        and completed
    )


async def process_text(text, language, session_id, db, *, source="text_test", asr_result=None, real_user=False):
    start=time.perf_counter(); language=normalize_language(language); text=redact(text.strip())
    journey=classify_journey(text); blocked=precheck(text)
    if blocked: response, natlas_llm=blocked, False
    else:
        try: response, natlas_llm = await generate(text, journey, language)
        except NAtlasLLMError as exc: raise HTTPException(status_code=503, detail=str(exc))
    response=(response+safety_suffix(journey)).strip()
    latency=int((time.perf_counter()-start)*1000)
    natlas_asr=bool(asr_result and asr_result.provider=="natlas")
    asr_provider="natlas" if natlas_asr else "none"; llm_provider="natlas" if natlas_llm else "stub"
    eligible = is_validation_eligible(
    source=source,
    natlas_asr=natlas_asr,
    real_user=real_user,
    completed=True,
)
    row=Interaction(session_id=session_id,language=language,journey=journey,transcript=text,response=response,
        interaction_source=source,asr_provider=asr_provider,llm_provider=llm_provider,real_user=real_user,
        completed=True,validation_eligible=eligible,asr_success=natlas_asr,natlas_asr=natlas_asr,
        natlas_llm=natlas_llm,latency_ms=latency,
        asr_model_id=(asr_result.model_id if asr_result else None),
        asr_mode=(asr_result.mode if asr_result else None),
        audio_duration_ms=(asr_result.duration_ms if asr_result else None),
        asr_latency_ms=(asr_result.asr_latency_ms if asr_result else None))
    db.add(row); db.commit(); db.refresh(row)
    return VoiceAnswer(interaction_id=row.id,language=language,transcript=text,journey=journey,response=response,
        interaction_source=source,asr_provider=asr_provider,llm_provider=llm_provider,validation_eligible=eligible,
        natlas_asr=natlas_asr,natlas_llm=natlas_llm,latency_ms=latency,
        asr_model_id=row.asr_model_id,asr_mode=row.asr_mode,audio_duration_ms=row.audio_duration_ms,asr_latency_ms=row.asr_latency_ms)

@router.post("/voice/ask",response_model=VoiceAnswer)
async def ask_voice(audio:UploadFile=File(...),language:str=Form("en-NG"),session_id:str=Form("web"),real_user:bool=Form(False),db:Session=Depends(get_db)):
    raw=await audio.read()
    if len(raw)>settings.max_audio_mb*1024*1024: raise HTTPException(413,"Audio file is too large")
    try: result=await transcribe(raw,audio.filename or "voice.wav",audio.content_type or "audio/wav",normalize_language(language))
    except (ASRNotConfigured, NAtlasASRError, AudioPreprocessError) as e: raise HTTPException(503,str(e))
    return await process_text(result.transcript,language,session_id,db,source="voice",asr_result=result,real_user=real_user)

@router.post("/text/test",response_model=VoiceAnswer)
async def text_test(body:TextTestIn,db:Session=Depends(get_db)):
    return await process_text(body.text,body.language,body.session_id,db,source="text_test",asr_result=None,real_user=False)
