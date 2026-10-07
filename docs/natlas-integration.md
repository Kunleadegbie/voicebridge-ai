# N-ATLAS Integration Evidence

## ASR
NAIC Problem Statement 02 requires official N-ATLAS ASR. `app/services/natlas_asr.py` is the isolated adapter. Until official endpoint documentation arrives, `NATLAS_ASR_MODE=pending` and voice requests return HTTP 503 rather than silently using a different ASR.

When documentation arrives, confirm: endpoint URL, auth header, multipart field name, supported audio formats, language identifiers, response schema, rate limits and retention/privacy terms. Then update only the adapter and `.env`.

## LLM
The public N-ATLAS model is `NCAIR1/N-ATLaS`. The app supports a configurable API adapter and a clearly labelled development stub. The stub is not competition integration and is recorded as `natlas_llm=false`.
