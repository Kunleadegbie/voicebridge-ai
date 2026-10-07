from fastapi import APIRouter, Depends
from sqlalchemy import select, func
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.db.models import Interaction
router=APIRouter()

def counts(db, column):
    rows=db.execute(select(column,func.count()).group_by(column)).all()
    return {str(k):v for k,v in rows}

@router.get("/interactions/summary")
def summary(db:Session=Depends(get_db)):
    total=db.scalar(select(func.count()).select_from(Interaction)) or 0
    eligible=db.scalar(select(func.count()).select_from(Interaction).where(Interaction.validation_eligible.is_(True))) or 0
    helpful=db.scalar(select(func.avg(Interaction.helpful)).where(Interaction.helpful.is_not(None)))
    understood_total=db.scalar(select(func.count()).select_from(Interaction).where(Interaction.understood.is_not(None))) or 0
    understood_yes=db.scalar(select(func.count()).select_from(Interaction).where(Interaction.understood.is_(True))) or 0
    return {"total_interactions":total,"documented_natlas_voice_interactions":eligible,"validation_target":50,
      "validation_progress_percent":min(round(eligible/50*100,1),100),
      "average_helpfulness":round(float(helpful),2) if helpful is not None else None,
      "understood_percent":round(understood_yes/understood_total*100,1) if understood_total else None,
      "by_language":counts(db,Interaction.language),"by_journey":counts(db,Interaction.journey),
      "by_source":counts(db,Interaction.interaction_source)}
