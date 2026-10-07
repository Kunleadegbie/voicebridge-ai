# VoiceBridge AI

**N-ATLAS-powered voice-first financial literacy for Nigerians**

VoiceBridge AI is a working prototype developed by **Chumcred Limited** for the **National AI Innovation Challenge (NAIC) 2026**, Innovation & Enterprise Track, **PS2: Voice-First Access**.

The application is designed to make basic financial knowledge more accessible to Nigerians who may be more comfortable speaking than typing, particularly in Nigerian languages.

## What VoiceBridge Does

A user selects a supported language and asks an everyday financial-literacy question by voice. VoiceBridge processes the interaction through a voice-first pipeline designed around N-ATLAS capabilities.

Supported languages:

- Nigerian-accented English
- Yoruba
- Hausa
- Igbo

Financial-literacy journeys:

1. Loans & Interest
2. Fraud & Scam Awareness
3. Savings
4. Digital Banking Safety
5. Small-Business Money
6. Everyday Financial Terms

## N-ATLAS Integration

VoiceBridge currently integrates the official NCAIR N-ATLAS speech-recognition model repositories:

- `NCAIR1/NigerianAccentedEnglish`
- `NCAIR1/Yoruba-ASR`
- `NCAIR1/Hausa-ASR`
- `NCAIR1/Igbo-ASR`

The ASR models are selected according to the user's chosen language and are loaded lazily.

End-to-end ASR testing has been completed across all four supported languages. Evidence is retained in:

`docs/evidence/sprint-2c/`

The application also contains an N-ATLAS multilingual LLM integration layer. Final hosted N-ATLAS LLM activation and acceptance testing are in progress.

## Current Prototype Status

Working now:

- Voice capture from the browser
- Four-language N-ATLAS ASR integration
- Automatic speech transcription
- Financial-literacy journey classification
- Safety controls
- Interaction logging
- N-ATLAS provenance tracking
- ASR diagnostics
- User-feedback capture
- Validation-eligibility controls
- Mobile-first user interface

In final integration/testing:

- Hosted N-ATLAS multilingual response generation
- Public deployment
- Real-user validation campaign

Development tests are not counted as real-user validation sessions.

## Validation Integrity

VoiceBridge distinguishes development activity from qualifying real-user voice interactions.

A validation interaction must be:

- voice-originated;
- processed with N-ATLAS ASR;
- performed by a real user; and
- completed successfully.

This prevents internal development tests from being represented as real-world validation.

## Safety

VoiceBridge is an educational financial-literacy tool. It does not:

- request PINs, passwords, OTPs, BVNs, CVVs or banking credentials;
- make lending or creditworthiness decisions;
- promise investment returns;
- recommend specific financial products or institutions; or
- provide personalised financial advice.

## Technology Stack

- Python
- FastAPI
- N-ATLAS ASR
- N-ATLAS LLM integration layer
- Hugging Face
- PyTorch
- SQLite
- HTML
- CSS
- JavaScript

## Repository Structure

- `backend/` - FastAPI application, N-ATLAS adapters, safety and persistence
- `frontend/` - mobile-first VoiceBridge interface
- `docs/` - architecture, integration, security and validation documentation
- `docs/evidence/` - preserved N-ATLAS ASR test evidence
- `scripts/` - diagnostics and test utilities
- `evidence/` - additional sprint evidence

## Running the Prototype

Create a Python virtual environment and install the required backend dependencies.

Configuration templates are provided in:

- `.env.example`
- `.env.cloud.example`

Actual credentials and environment secrets are intentionally excluded from this repository.

The first use of a local ASR model may require downloading the corresponding gated N-ATLAS model from Hugging Face. Appropriate model access must already be configured.

## Evidence and Documentation

Useful evaluator references:

- `docs/architecture.md`
- `docs/natlas-integration.md`
- `docs/sprint-2c-asr.md`
- `docs/validation-plan.md`
- `docs/SECURITY.md`
- `docs/privacy.md`
- `docs/evidence/sprint-2c/SPRINT-2C-CLOSURE.md`
- `docs/evidence/sprint-2c/asr-tests/four-language-end-to-end-asr-evidence.md`

## NAIC 2026

**Track:** Innovation & Enterprise  
**Problem Statement:** PS2 - Voice-First Access  
**Use Case:** Financial Literacy  
**Delivery Channel:** Low-bandwidth mobile application  
**Applicant:** Chumcred Limited  
**Project:** VoiceBridge AI

## Status Notice

This repository represents an actively developed NAIC 2026 working prototype. Features and validation evidence will continue to be updated before final submission.

---

**VoiceBridge AI**  
*Financial knowledge in your language. Through your voice.*
