
from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import Response
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.db.models import Interaction
from app.services.speech_cache import get_or_generate_speech
from app.services.speech_auth import verify_speech_token
from app.services.speech_usage import SpeechLimitExceeded


router = APIRouter(
    prefix="/tts",
    tags=["Text to Speech"],
)


class SpeechRequest(BaseModel):
    interaction_id: str
    speech_token: str


@router.post("/speak")
def speak(
    request: SpeechRequest,
    db: Session = Depends(get_db),
):
    # Step 1: Verify that the request is authorized.
    if not verify_speech_token(
        request.interaction_id,
        request.speech_token,
    ):
        raise HTTPException(
            status_code=403,
            detail="Invalid or expired speech authorization",
        )

    # Step 2: Retrieve the original interaction.
    interaction = db.get(
        Interaction,
        request.interaction_id,
    )

    if interaction is None:
        raise HTTPException(
            status_code=404,
            detail="Interaction not found",
        )

    # Step 3: Validate the answer before generating audio.
    if (
        not interaction.response
        or not interaction.response.strip()
    ):
        raise HTTPException(
            status_code=400,
            detail="No spoken answer is available",
        )

    if len(interaction.response) > 2000:
        raise HTTPException(
            status_code=400,
            detail="Answer exceeds the speech safety limit",
        )

    # Step 4: Retrieve cached audio or generate new audio.
    try:
        audio = get_or_generate_speech(
            interaction_id=interaction.id,
            text=interaction.response,
            language=interaction.language,
        )

        return Response(
            content=audio,
            media_type="audio/mpeg",
            headers={
                "Cache-Control": "no-store",
            },
        )

    # Step 5: Handle exhausted speech-generation allowances.
    except SpeechLimitExceeded as exc:
        raise HTTPException(
            status_code=429,
            detail=str(exc),
            headers={
                "Retry-After": "3600",
            },
        )

    # Step 6: Handle invalid speech-generation input.
    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )

    # Step 7: Handle unexpected speech-provider errors.
    except Exception:
        raise HTTPException(
            status_code=502,
            detail="Speech generation is temporarily unavailable",
        )
