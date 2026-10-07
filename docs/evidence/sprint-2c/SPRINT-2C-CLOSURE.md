# VoiceBridge AI — Sprint 2C Closure Manifest

## Sprint
Sprint 2C — Official N-ATLAS ASR Integration
Closure phase: Sprint 2C.1 — Stabilization & Evidence Lock
Status: CLOSED — DEVELOPMENT MILESTONE PASSED
Closure date: 28 September 2026

## Objective
Integrate and development-test the official NCAIR1 ASR repositories used by VoiceBridge AI across the four target languages:

- Nigerian English
- Yoruba
- Hausa
- Igbo

The sprint also establishes provenance controls that separate development activity from future NAIC real-user validation.

## ASR Model Registry

| Language | Code | Model |
|---|---|---|
| Nigerian English | en-NG | NCAIR1/NigerianAccentedEnglish |
| Yoruba | yo-NG | NCAIR1/Yoruba-ASR |
| Hausa | ha-NG | NCAIR1/Hausa-ASR |
| Igbo | ig-NG | NCAIR1/Igbo-ASR |

## End-to-End Development Result

Nigerian English: PASS

Yoruba: PASS WITH TRANSCRIPTION IMPERFECTIONS

Hausa: PASS AFTER DOWNSTREAM ACRONYM NORMALIZATION

Igbo: PASS WITH TRANSCRIPTION IMPERFECTIONS

All four target ASR integrations successfully completed the VoiceBridge development path.

This result does not claim perfect transcription accuracy.

## Automated Regression Gate

Final Sprint 2C.1 regression result:

13 tests collected
13 tests passed
0 tests failed

Coverage includes:

- Six financial-literacy journeys
- Out-of-scope handling
- Financial-term explanation
- Sensitive-data redaction
- Product/recommendation guardrails
- ASR security-acronym normalization
- SCAM response de-duplication
- N-ATLAS prompt/runtime safeguards
- Four-language ASR registry
- WAV/audio preprocessing
- Project .env path
- Validation eligibility protection

## Validation Provenance Rule

An interaction qualifies for the future NAIC real-user validation count only when all required conditions are satisfied:

1. interaction source = voice
2. N-ATLAS ASR successfully used
3. real_user = true
4. interaction completed successfully

Development and text-test interactions remain excluded.

## Database Baseline at Closure

Total development interactions: 20

Text-test interactions: 10

Voice interactions: 10

Qualifying N-ATLAS real-user validation interactions: 0

Validation target: 50

Validation progress: 0%

The zero validation count is intentional and confirms that development interactions have not contaminated the future competition-validation dataset.

Historical OTHER classifications have been retained as engineering evidence rather than deleted.

## Current Architecture Boundary

N-ATLAS ASR:
IMPLEMENTED AND DEVELOPMENT-TESTED

N-ATLAS LLM:
NOT YET ACTIVE

Current development response provider:
STUB

Cloud N-ATLAS LLM deployment:
DEFERRED

Runpod paid inference:
NOT REQUIRED FOR SPRINT 2C CLOSURE

## Known Limitations

1. Yoruba and Igbo development tests showed transcription/orthographic imperfections while retaining sufficient meaning for the tested scenario.

2. Hausa testing exposed a downstream classification issue when OTP was transcribed as a punctuated acronym such as O.T.P. Normalization was added and regression-tested.

3. Development testing is not a substitute for the required real-user validation exercise.

4. N-ATLAS LLM integration remains outstanding.

5. Local deployment uses official NCAIR1 Hugging Face ASR repositories, but whether this satisfies the NAIC wording "official N-ATLAS ASR service" remains subject to organizer confirmation.

## Evidence Inventory

### Database
database/

Contains the timestamped interaction-summary snapshot captured at Sprint 2C closure.

### Automated Tests
test-results/

Contains the timestamped full pytest regression output demonstrating 13/13 passing tests.

### Configuration
configuration/

Contains sanitized N-ATLAS ASR runtime diagnostics and four-language model mappings.

No .env file, API key, Hugging Face token or other secret should be stored here.

### ASR Tests
asr-tests/four-language-end-to-end-asr-evidence.md

Contains the human-readable four-language end-to-end development evidence and observed limitations.

## Evidence Integrity Principles

VoiceBridge evidence must:

- distinguish development tests from real-user validation;
- preserve unsuccessful and imperfect engineering observations where relevant;
- never inflate interaction counts;
- never represent STUB responses as N-ATLAS LLM output;
- never represent self-hosted ASR as satisfying a hosted-service requirement unless confirmed by NAIC/NCAIR;
- exclude passwords, API keys, tokens and other secrets from evidence artefacts.

## Closure Decision

Sprint 2C.1 — Stabilization & Evidence Lock is CLOSED.

The VoiceBridge AI codebase has passed its development regression gate and demonstrated end-to-end ASR integration across Nigerian English, Yoruba, Hausa and Igbo.

The next development phase may proceed without altering this historical evidence package.

## Next Phase

Sprint 2D — N-ATLAS Multilingual Intelligence Integration

Planned objectives:

- replace STUB response generation with genuine N-ATLAS inference;
- preserve the existing financial-literacy safety layer;
- verify response-language behaviour across all four target languages;
- verify all six financial-literacy journeys;
- preserve provider provenance;
- keep development interactions excluded from real-user validation;
- activate paid cloud inference only when technically necessary.

Real-user validation begins only after the production candidate is sufficiently stable for controlled testing.
