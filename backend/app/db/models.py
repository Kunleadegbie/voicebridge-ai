import uuid
from datetime import datetime, timezone
from sqlalchemy import String, Text, Boolean, Integer, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from app.db.database import Base

class Interaction(Base):
    __tablename__ = "interactions"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    session_id: Mapped[str] = mapped_column(String(64), index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    language: Mapped[str] = mapped_column(String(16), default="en-NG", index=True)
    journey: Mapped[str] = mapped_column(String(16), default="OTHER", index=True)
    transcript: Mapped[str] = mapped_column(Text, default="")
    response: Mapped[str] = mapped_column(Text, default="")
    interaction_source: Mapped[str] = mapped_column(String(20), default="text_test", index=True)
    asr_provider: Mapped[str] = mapped_column(String(20), default="none", index=True)
    llm_provider: Mapped[str] = mapped_column(String(20), default="stub", index=True)
    real_user: Mapped[bool] = mapped_column(Boolean, default=False)
    completed: Mapped[bool] = mapped_column(Boolean, default=True)
    validation_eligible: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    asr_success: Mapped[bool] = mapped_column(Boolean, default=False)
    natlas_asr: Mapped[bool] = mapped_column(Boolean, default=False)
    natlas_llm: Mapped[bool] = mapped_column(Boolean, default=False)
    latency_ms: Mapped[int] = mapped_column(Integer, default=0)
    asr_model_id: Mapped[str | None] = mapped_column(String(128), nullable=True)
    asr_mode: Mapped[str | None] = mapped_column(String(20), nullable=True)
    audio_duration_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)
    asr_latency_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)
    understood: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    helpful: Mapped[int | None] = mapped_column(Integer, nullable=True)
    asr_correct: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    optional_comment: Mapped[str | None] = mapped_column(Text, nullable=True)
