# VoiceBridge AI Architecture

Mobile browser -> MediaRecorder -> FastAPI `/api/v1/voice/ask` -> official N-ATLAS ASR adapter -> transcript -> journey classifier -> N-ATLAS LLM adapter -> safety layer -> response -> SQLite/PostgreSQL interaction log -> feedback.

The ASR adapter intentionally fails closed until the official NAIC/NCAIR ASR endpoint is configured. No substitute speech model is presented as N-ATLAS.
