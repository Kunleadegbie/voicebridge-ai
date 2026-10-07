# Sprint 2B Track A — N-ATLAS LLM Integration Readiness

## Objective
Prepare VoiceBridge AI for genuine N-ATLAS LLM inference without waiting for the official ASR contract.

## Decision
The preferred competition deployment route is an official or hosted N-ATLAS API.

The public N-ATLAS model is an 8B Llama-family model distributed in BF16. Full local loading is therefore a hardware-heavy development option, not the default competition route.

## Modes

### stub
Safe development mode. No N-ATLAS claim is made.

### api
Uses an OpenAI-compatible adapter:
- NATLAS_LLM_URL
- NATLAS_LLM_API_KEY
- NATLAS_MODEL_NAME

If the eventual NCAIR contract differs, only `app/services/natlas_llm.py` needs to change.

### local
Loads `NCAIR1/N-ATLaS` through Hugging Face Transformers. Model access requires accepting the repository conditions and may require a Hugging Face token.

Install:
`pip install -r backend/requirements-local.txt`

Then configure:
`NATLAS_LLM_MODE=local`
`NATLAS_HF_TOKEN=...`

Do not install local-model dependencies merely to run the normal web application.

## Hardware probe
Run:
`powershell -ExecutionPolicy Bypass -File .\scripts\check_hardware.ps1`

Then run VoiceBridge and query:
`GET /providers/status`

## Acceptance criteria
1. Existing six text journeys continue to pass.
2. `/providers/status` reports the selected provider and local hardware readiness.
3. Stub interactions remain marked `LLM: STUB`.
4. API/local mode marks successful generations as N-ATLAS.
5. Provider failures return HTTP 503 rather than silently pretending the stub is N-ATLAS.
