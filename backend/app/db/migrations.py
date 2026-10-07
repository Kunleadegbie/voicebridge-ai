from sqlalchemy import inspect, text
from app.db.database import engine

# Lightweight SQLite-safe Sprint 2A migration. Keeps existing Sprint 1 interactions.
COLUMNS = {
    "interaction_source": "VARCHAR(20) DEFAULT 'text_test'",
    "asr_provider": "VARCHAR(20) DEFAULT 'none'",
    "llm_provider": "VARCHAR(20) DEFAULT 'stub'",
    "real_user": "BOOLEAN DEFAULT 0",
    "completed": "BOOLEAN DEFAULT 1",
    "validation_eligible": "BOOLEAN DEFAULT 0",
    "asr_model_id": "VARCHAR(128)",
    "asr_mode": "VARCHAR(20)",
    "audio_duration_ms": "INTEGER",
    "asr_latency_ms": "INTEGER",
}

def migrate():
    inspector = inspect(engine)
    if "interactions" not in inspector.get_table_names():
        return
    existing = {c["name"] for c in inspector.get_columns("interactions")}
    with engine.begin() as conn:
        for name, ddl in COLUMNS.items():
            if name not in existing:
                conn.execute(text(f"ALTER TABLE interactions ADD COLUMN {name} {ddl}"))
