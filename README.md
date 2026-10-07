# VoiceBridge AI — Sprint 2C

Voice-first financial-literacy MVP for NAIC 2026. Sprint 2C adds real local inference against the official NCAIR1 N-ATLAS ASR repositories while retaining the Sprint 2A financial engine and Sprint 2B LLM adapter.

## Important
The first model load downloads the selected gated model from Hugging Face. Models are loaded lazily: the Nigerian-English first test does **not** download Yoruba, Hausa or Igbo. Hugging Face CLI login/access must already be valid.

See `docs/sprint-2c-asr.md` for scope and `backend/requirements-asr.txt` for the separate ASR dependencies.
