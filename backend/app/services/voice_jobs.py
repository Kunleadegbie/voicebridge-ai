import asyncio
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone, timedelta

@dataclass
class VoiceJob:
    status: str = "processing"
    result: dict | None = None
    error: str | None = None
    created_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

jobs: dict[str, VoiceJob] = {}

MAX_ACTIVE_JOBS = 5

def create_job() -> str:
    cutoff = datetime.now(timezone.utc) - timedelta(minutes=30)

    for existing_id, existing_job in list(jobs.items()):
        if (
            existing_job.status in ("completed", "failed")
            and existing_job.created_at < cutoff
        ):
            del jobs[existing_id]

    active_jobs = sum(
        job.status == "processing"
        for job in jobs.values()
    )

    if active_jobs >= MAX_ACTIVE_JOBS:
        raise RuntimeError(
            "Voice queue is full. Please try again shortly."
        )

    job_id = uuid.uuid4().hex
    jobs[job_id] = VoiceJob()
    return job_id

def get_job(job_id: str) -> VoiceJob | None:
    return jobs.get(job_id)

def complete_job(job_id: str, result: dict) -> None:
    job = jobs.get(job_id)
    if job:
        job.status = "completed"
        job.result = result

def fail_job(job_id: str, error: str) -> None:
    job = jobs.get(job_id)
    if job:
        job.status = "failed"
        job.error = error
