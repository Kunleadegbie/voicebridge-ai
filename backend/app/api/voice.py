
import asyncio
import time

from fastapi import APIRouter, UploadFile, File, Form, Depends, HTTPException
from sqlalchemy.orm import Session

from app.config import settings
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
from app.services.speech_auth import create_speech_token

from app.services.voice_usage import (
    reserve_voice_request,
    VoiceLimitExceeded,
)


router = APIRouter()
voice_processing_lock = asyncio.Lock()


def is_validation_eligible(
    source: str,
    natlas_asr: bool,
    real_user: bool,
    completed: bool = True,
) -> bool:
    """
    An interaction qualifies for real-user validation only when:
    - it is a voice interaction,
    - official N-ATLAS ASR was successfully used,
    - it is marked as a real-user interaction, and
    - the interaction completed successfully.
    """
    return bool(
        source == "voice"
        and natlas_asr
        and real_user
        and completed
    )


async def process_text(
    text,
    language,
    session_id,
    db,
    *,
    source="text_test",
    asr_result=None,
    real_user=False,
):
    start = time.perf_counter()

    language = normalize_language(language)
    text = redact(text.strip())

    journey = classify_journey(text)
    blocked = precheck(text)

    if blocked:
        response = blocked
        natlas_llm = False
    else:
        try:
            response, natlas_llm = await generate(
                text,
                journey,
                language,
            )
        except NAtlasLLMError as exc:
            raise HTTPException(
                status_code=503,
                detail=str(exc),
            )

    response = (
        response + safety_suffix(journey)
    ).strip()

    latency = int(
        (time.perf_counter() - start) * 1000
    )

    natlas_asr = bool(
        asr_result
        and asr_result.provider == "natlas"
    )

    asr_provider = "natlas" if natlas_asr else "none"
    llm_provider = "natlas" if natlas_llm else "stub"

    eligible = is_validation_eligible(
        source=source,
        natlas_asr=natlas_asr,
        real_user=real_user,
        completed=True,
    )

    row = Interaction(
        session_id=session_id,
        language=language,
        journey=journey,
        transcript=text,
        response=response,
        interaction_source=source,
        asr_provider=asr_provider,
        llm_provider=llm_provider,
        real_user=real_user,
        completed=True,
        validation_eligible=eligible,
        asr_success=natlas_asr,
        natlas_asr=natlas_asr,
        natlas_llm=natlas_llm,
        latency_ms=latency,
        asr_model_id=(
            asr_result.model_id
            if asr_result
            else None
        ),
        asr_mode=(
            asr_result.mode
            if asr_result
            else None
        ),
        audio_duration_ms=(
            asr_result.duration_ms
            if asr_result
            else None
        ),
        asr_latency_ms=(
            asr_result.asr_latency_ms
            if asr_result
            else None
        ),
    )

    db.add(row)
    db.commit()
    db.refresh(row)

    return VoiceAnswer(
        interaction_id=row.id,
        speech_token=create_speech_token(row.id),
        language=language,
        transcript=text,
        journey=journey,
        response=response,
        interaction_source=source,
        asr_provider=asr_provider,
        llm_provider=llm_provider,
        validation_eligible=eligible,
        natlas_asr=natlas_asr,
        natlas_llm=natlas_llm,
        latency_ms=latency,
        asr_model_id=row.asr_model_id,
        asr_mode=row.asr_mode,
        audio_duration_ms=row.audio_duration_ms,
        asr_latency_ms=row.asr_latency_ms,
    )


@router.post(
    "/voice/ask",
    response_model=VoiceAnswer,
)

async def ask_voice(
    audio: UploadFile = File(...),
    language: str = Form("en-NG"),
    session_id: str = Form("web"),
    real_user: bool = Form(False),
    db: Session = Depends(get_db),
):
    raw = await audio.read()

    if len(raw) > settings.max_audio_mb * 1024 * 1024:
        raise HTTPException(
            status_code=413,
            detail="Audio file is too large",
        )

    if voice_processing_lock.locked():
        raise HTTPException(
            status_code=429,
            detail="Voice processing is busy. Please try again shortly.",
        )

    async with voice_processing_lock:
        try:
            reserve_voice_request()
        except VoiceLimitExceeded as exc:
            raise HTTPException(
                status_code=429,
                detail=str(exc),
            ) from exc

        try:
            result = await transcribe(
                raw,
                audio.filename or "voice.wav",
                audio.content_type or "audio/wav",
                normalize_language(language),
            )
        except (
            ASRNotConfigured,
            NAtlasASRError,
            AudioPreprocessError,
        ) as exc:
            raise HTTPException(
                status_code=503,
                detail=str(exc),
            ) from exc

        return await process_text(
            result.transcript,
            language,
            session_id,
            db,
            source="voice",
            asr_result=result,
            real_user=real_user,
        )

@router.post(
    "/text/test",
    response_model=VoiceAnswer,
)
async def text_test(
    body: TextTestIn,
    db: Session = Depends(get_db),
):
    if not settings.enable_text_test:
        raise HTTPException(
            status_code=404,
            detail="Text testing is disabled",
        )

    return await process_text(
        body.text,
        body.language,
        body.session_id,
        db,
        source="text_test",
        asr_result=None,
        real_user=False,
    )

from fastapi.encoders import jsonable_encoder
from app.db.database import SessionLocal
from app.services.voice_jobs import (
    create_job,
    get_job,
    complete_job,
    fail_job,
)



async def process_voice_job(
    job_id: str,
    raw: bytes,
    filename: str,
    content_type: str,
    language: str,
    session_id: str,
    real_user: bool,
):
    db = SessionLocal()

    try:
        async with voice_processing_lock:
            reserve_voice_request()

            result = await transcribe(
                raw,
                filename,
                content_type,
                normalize_language(language),
            )

            answer = await process_text(
                result.transcript,
                language,
                session_id,
                db,
                source="voice",
                asr_result=result,
                real_user=real_user,
            )

        complete_job(
            job_id,
            jsonable_encoder(answer),
        )

    except Exception as exc:
        print(
            f"[VOICE JOB] {job_id} failed: {exc}",
            flush=True,
        )
        fail_job(
            job_id,
            "Voice processing could not be completed. "
            "Please contact the test coordinator.",
        )

    finally:
        db.close()


@router.post("/voice/submit", status_code=202)
async def submit_voice(
    audio: UploadFile = File(...),
    language: str = Form("en-NG"),
    session_id: str = Form("web"),
    real_user: bool = Form(False),
):
    raw = await audio.read()

    if not raw:
        raise HTTPException(
            status_code=400,
            detail="Audio recording is empty.",
        )

    if len(raw) > settings.max_audio_mb * 1024 * 1024:
        raise HTTPException(
            status_code=413,
            detail="Audio file is too large.",
        )

    try:
        job_id = create_job()
    except RuntimeError as exc:
        raise HTTPException(
            status_code=429,
            detail=str(exc),
        ) from exc

    asyncio.create_task(
        process_voice_job(
            job_id,
            raw,
            audio.filename or "voice.wav",
            audio.content_type or "audio/wav",
            language,
            session_id,
            real_user,
        )
    )

    return {
        "job_id": job_id,
        "status": "processing",
    }


@router.get("/voice/status/{job_id}")
async def voice_job_status(job_id: str):
    job = get_job(job_id)

    if job is None:
        raise HTTPException(
            status_code=404,
            detail="Voice request not found.",
        )

    if job.status == "completed":
        return {
            "status": "completed",
            "result": job.result,
        }

    if job.status == "failed":
        return {
            "status": "failed",
            "error": job.error,
        }

    return {
        "status": "processing",
    }
