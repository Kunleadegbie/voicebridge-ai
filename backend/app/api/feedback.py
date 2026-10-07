from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.db.models import Interaction
from app.schemas.interaction import FeedbackIn
router=APIRouter()
@router.post("/feedback")
def feedback(body: FeedbackIn, db: Session=Depends(get_db)):
    row=db.get(Interaction, body.interaction_id)
    if not row: raise HTTPException(404,"Interaction not found")
    row.understood=body.understood; row.helpful=body.helpful; row.asr_correct=body.asr_correct; row.optional_comment=body.comment
    db.commit(); return {"status":"saved"}
