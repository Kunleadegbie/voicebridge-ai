from pydantic import BaseModel, Field

class VoiceAnswer(BaseModel):
    interaction_id: str
    language: str
    transcript: str
    journey: str
    response: str
    interaction_source: str
    asr_provider: str
    llm_provider: str
    validation_eligible: bool
    natlas_asr: bool
    natlas_llm: bool
    latency_ms: int
    asr_model_id: str | None = None
    asr_mode: str | None = None
    audio_duration_ms: int | None = None
    asr_latency_ms: int | None = None

class FeedbackIn(BaseModel):
    interaction_id: str
    understood: bool | None = None
    helpful: int | None = Field(default=None, ge=1, le=5)
    asr_correct: bool | None = None
    comment: str | None = Field(default=None, max_length=1000)
