# VoiceBridge AI — System Architecture

**Project:** VoiceBridge AI
**Purpose:** Voice-first financial literacy for Nigerian users
**Architecture status:** Implemented prototype
**Documentation date:** 9 October 2026

## 1. System Overview

VoiceBridge AI is a browser-based application that enables users to ask financial-literacy questions through voice interaction.

The application is designed around four language options:

- Nigerian English (`en-NG`)
- Yoruba (`yo-NG`)
- Hausa (`ha-NG`)
- Igbo (`ig-NG`)

The application uses a FastAPI backend, N-ATLAS speech recognition, an N-ATLAS language model, financial-literacy response processing and an interaction-recording system.

## 2. Processing Architecture

The principal voice-processing sequence is:

**Mobile Browser → Audio Recording → FastAPI Backend → N-ATLAS ASR → Transcript → Financial-Literacy Processing → N-ATLAS LLM → Response Processing → Browser Display**

Interaction metadata and participant feedback are recorded for monitoring and validation.

## 3. Frontend

The frontend uses HTML and JavaScript.

Its functions include:

- Language selection
- Browser microphone recording
- Submission of recorded speech
- Display of recognized speech and generated answers
- User feedback collection
- Participant self-declaration for validation
- Error handling for interrupted requests

## 4. Backend

The backend is implemented with Python and FastAPI.

Its responsibilities include:

- Receiving voice requests
- Managing speech recognition
- Invoking the language-model service
- Processing financial-literacy questions
- Recording interactions
- Providing validation and reporting endpoints

## 5. N-ATLAS Speech Recognition

VoiceBridge AI uses a locally executed N-ATLAS ASR integration.

The configured execution mode is:

`NATLAS_ASR_MODE=local`

The current development environment runs speech recognition on CPU.

Speech-recognition latency depends on recording length and available computing resources.

## 6. N-ATLAS Language Model

The application integrates the N-ATLAS language model through a Runpod-hosted API service.

The configured execution mode is:

`NATLAS_LLM_MODE=api`

The integration submits requests to the hosted inference service and polls for completion.

Runpod queue delays, model execution time and network conditions can affect response latency.

## 7. Interaction Logging and Validation

The application records interaction metadata, including language, interaction source, model-provider indicators, completion status and feedback.

Developer tests and genuine participant interactions are distinguished.

Participant eligibility is recorded using the application's validation controls; participant self-declaration is not equivalent to independent identity verification.

The current validation target is 50 documented qualifying voice interactions.

## 8. Deployment

The current prototype runs on a local FastAPI server and is exposed for remote testing through a temporary Cloudflare Quick Tunnel.

This arrangement is suitable for controlled prototype demonstrations but is not a permanent production-hosting configuration.

The public tunnel depends on the local backend and tunnel processes remaining available.

## 9. Known Limitations

- Local CPU speech recognition can introduce noticeable processing delays.
- Hosted LLM inference may experience queueing and execution delays.
- Long-running voice requests may be interrupted by the browser or temporary tunnel.
- Public testing depends on the availability of the local development machine.
- Real-user validation remains in progress.

## 10. Verification Status

As of 9 October 2026:

- The backend has started successfully.
- The public application has returned HTTP 200.
- The JavaScript syntax check has passed.
- All 17 automated backend tests have passed.
- N-ATLAS voice integration has been exercised during development.
- The 50-interaction participant-validation target has not yet been achieved.

These checks establish prototype functionality but do not constitute proof of production readiness or completion of participant validation.