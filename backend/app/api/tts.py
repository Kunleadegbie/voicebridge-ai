from fastapi import APIRouter, HTTPException
from fastapi.responses import Response
from pydantic import BaseModel, Field

from app.services.spitch_tts import generate_speech

router = APIRouter(prefix="/tts", tags=["Text to Speech"])


class SpeechRequest(BaseModel):
    text: str = Field(min_length=1, max_length=2000)
    language: str


@router.post("/speak")
def speak(request: SpeechRequest):
    try:
        audio = generate_speech(
            text=request.text,
            language=request.language,
        )

        return Response(
            content=audio,
            media_type="audio/mpeg",
            headers={"Cache-Control": "no-store"},
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )

    except Exception:
        # Do not expose API keys or provider error details.
        raise HTTPException(
            status_code=502,
            detail="Speech generation is temporarily unavailable",
        )