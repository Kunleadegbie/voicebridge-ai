# VoiceBridge AI — NAIC Validation Plan (Sprint 2A)

## Eligibility rule
An interaction counts toward the competition voice-validation target only when all are true:
- `interaction_source == voice`
- `asr_provider == natlas`
- `real_user == true`
- `completed == true`

Developer text tests never count. Stub-model use is disclosed in provenance fields.

## Target
Minimum target in the product dashboard: 50 documented eligible N-ATLAS voice interactions. Operational target: 75 interactions to provide margin.

## Evidence captured
Anonymous session ID, timestamp, language, journey, transcript, response, interaction source, ASR provider, LLM provider, validation eligibility, latency, comprehension feedback, helpfulness, ASR correctness and optional comment.

## Privacy
Do not request names, phone numbers, BVNs, account numbers, PINs, passwords, OTPs, card numbers or CVVs. Numeric identifiers are redacted where detected.
