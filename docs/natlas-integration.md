
# VoiceBridge AI — N-ATLAS Integration Evidence

**Project:** VoiceBridge AI
**Documentation date:** 9 October 2026
**Status:** Implemented prototype; participant validation ongoing

## 1. Integration Overview

VoiceBridge AI integrates N-ATLAS speech recognition and
N-ATLAS language generation into a voice-first financial
literacy application.

The two components use different execution environments:

- ASR: Local inference on CPU
- LLM: Runpod-hosted inference API

Both integrations are implemented through dedicated
Python service modules.

## 2. N-ATLAS Automatic Speech Recognition

Service module:
`backend/app/services/natlas_asr.py`

Active configuration:
`NATLAS_ASR_MODE=local`
`NATLAS_ASR_DEVICE=cpu`

The ASR component processes submitted audio and returns
a transcript for downstream question processing.

The application supports language selection for:

- Nigerian English: en-NG
- Yoruba: yo-NG
- Hausa: ha-NG
- Igbo: ig-NG

These are application language options; their presence
does not independently establish equal recognition
accuracy across all four languages.

## 3. N-ATLAS Language Model

Service module:
`backend/app/services/natlas_llm.py`

Model family:
`NCAIR1/N-ATLaS`

Active configuration:
`NATLAS_LLM_MODE=api`

The application uses a Runpod-hosted inference service.

Processing sequence:

1. Receive the recognized transcript.
2. Prepare the financial-literacy question and context.
3. Submit an inference request to Runpod.
4. Poll the inference job until completion or failure.
5. Parse the generated response.
6. Return the result to the application.

The current configured maximum output length is
120 tokens.

## 4. Performance Monitoring

The LLM adapter includes diagnostic logging for:

- Total elapsed inference-request time
- Runpod queue delay, when reported
- Runpod execution time, when reported
- Configured maximum output tokens

These measurements are printed to the backend console.

They are not currently a comprehensive, persistent
performance-monitoring dataset.

## 5. Interaction Evidence

The application records interaction information,
including:

- Language
- Interaction source
- ASR and LLM provider indicators
- Completion status
- Validation eligibility
- ASR and overall processing latency fields
- Participant feedback, when submitted

The validation dashboard distinguishes developer tests
from qualifying participant voice interactions.

As of the latest recorded baseline on 9 October 2026:

- Total recorded interactions: 26
- Recorded voice interactions: 19
- Recorded text tests: 7
- Documented qualifying participant voice interactions: 0
- Validation target: 50

These figures represent a dated baseline and must be
updated before final submission.

## 6. Verification Evidence

The following checks have been completed:

- Python syntax validation for the LLM adapter
- JavaScript syntax validation for the frontend
- Successful FastAPI startup
- Successful public HTTP 200 response
- 17 passing automated backend tests
- Development-stage voice interactions using the
  integrated processing pipeline

Automated test success does not establish multilingual
ASR accuracy, reliable end-to-end latency or completion
of real-user validation.

## 7. Known Limitations

Local CPU-based speech recognition may be slow.

Runpod inference may experience queue delays or long
execution times.

Temporary Cloudflare tunnel connections may be
interrupted during long-running requests.

The application does not yet have a production-grade
asynchronous job and response-retrieval mechanism.

## 8. Security and Evidence Handling

API credentials and other secrets are configured
outside the published source code.

Credentials, private environment files and access
tokens must not be included in submission documents,
screenshots or public Git commits.

Real-user evidence must reflect actual participant
activity. Developer tests must not be presented as
independent participant validation.

## 9. Remaining Validation Work

Before final competition submission:

- Collect genuine participant voice interactions.
- Review language coverage and response quality.
- Document observed errors and latency.
- Update validation metrics.
- Prepare a demonstration showing the actual system.
- Clearly disclose unresolved prototype limitations.

## 10. Conclusion

VoiceBridge AI has implemented a working prototype
integration of N-ATLAS speech recognition and
N-ATLAS language generation.

Its integration and automated tests have been exercised,
but real-user validation and performance assessment
remain ongoing.
