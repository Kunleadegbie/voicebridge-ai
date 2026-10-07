# Connect the existing VoiceBridge backend

Your Sprint 2B Track A adapter already speaks the OpenAI-compatible chat API.

Once the cloud endpoint is available over HTTPS, edit the existing
`voicebridge-ai/.env` locally:

NATLAS_LLM_MODE=api
NATLAS_LLM_URL=https://YOUR_HOST/v1/chat/completions
NATLAS_LLM_API_KEY=YOUR_INFERENCE_API_KEY
NATLAS_MODEL_NAME=NCAIR1/N-ATLaS

Restart Uvicorn.

Then test:
`What does collateral mean?`

Expected VoiceBridge provenance:
- ASR: NONE
- LLM: N-ATLAS
- TEST ONLY

The `TEST ONLY` status is correct. It must not count toward the NAIC real-user
voice validation total until official N-ATLAS ASR is also in the path.

If the cloud provider returns an error, VoiceBridge should return HTTP 503.
It must never silently relabel a stub answer as N-ATLAS.
