from pathlib import Path
from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from app.db.database import Base, engine
from app.db.migrations import migrate
from app.api import health, voice, feedback, interactions, tts

Base.metadata.create_all(bind=engine); migrate()
app=FastAPI(title="VoiceBridge AI",description="Voice-first financial literacy powered by N-ATLAS",version="0.2.2")
app.include_router(health.router)
app.include_router(voice.router)
app.include_router(feedback.router)
app.include_router(interactions.router)
app.include_router(tts.router)

PROJECT_ROOT=Path(__file__).resolve().parents[2]; FRONTEND_DIR=PROJECT_ROOT/"frontend"
if not FRONTEND_DIR.exists(): raise RuntimeError(f"Frontend directory not found: {FRONTEND_DIR}")
app.mount("/static",StaticFiles(directory=str(FRONTEND_DIR)),name="static")
@app.get("/",include_in_schema=False)
async def home(): return FileResponse(FRONTEND_DIR/"index.html")
