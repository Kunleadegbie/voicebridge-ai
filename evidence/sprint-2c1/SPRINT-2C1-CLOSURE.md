\# VoiceBridge AI

\## Sprint 2C.1 - Stabilization and Evidence Lock



\*\*Project:\*\* VoiceBridge AI  

\*\*Applicant:\*\* Chumcred Limited  

\*\*Competition:\*\* National AI Innovation Challenge (NAIC) 2026  

\*\*Track:\*\* Innovation \& Enterprise  

\*\*Problem Statement:\*\* Voice-First Access  

\*\*Domain:\*\* Basic Financial Literacy / Financial Inclusion  

\*\*Sprint Status:\*\* CLOSED - PASS  

\*\*Closure Date:\*\* 27 September 2026  



\---



\## 1. Sprint Objective



Sprint 2C.1 was undertaken to stabilize the VoiceBridge AI N-ATLAS speech-recognition integration before proceeding to multilingual N-ATLAS intelligence integration.



The sprint focused on:



\- preserving the working four-language ASR integration;

\- correcting defects identified during live development testing;

\- strengthening validation provenance;

\- preventing development interactions from being counted as real-user validation;

\- establishing automated regression protection; and

\- creating a reproducible technical evidence baseline.



\---



\## 2. Supported Voice Languages



VoiceBridge AI currently integrates the following NCAIR1 ASR model repositories:



| Language | Code | ASR Model |

|---|---|---|

| Nigerian English | en-NG | NCAIR1/NigerianAccentedEnglish |

| Yoruba | yo-NG | NCAIR1/Yoruba-ASR |

| Hausa | ha-NG | NCAIR1/Hausa-ASR |

| Igbo | ig-NG | NCAIR1/Igbo-ASR |



All four language paths were exercised end-to-end during development testing.



\---



\## 3. Current ASR Runtime



At Sprint 2C.1 closure:



\- ASR mode: local

\- Device preference: CPU

\- PyTorch installed: yes

\- Transformers installed: yes

\- CUDA available: no

\- GPU: none detected

\- Model loading: lazy and cached in process

\- Hosted ASR API configured: no



The local implementation uses the identified NCAIR1 Hugging Face ASR repositories.



Competition interpretation of the phrase "official N-ATLAS ASR service" remains subject to confirmation from NAIC/NCAIR. No claim is made in this closure record that local deployment alone resolves that competition-compliance question.



\---



\## 4. Four-Language Development Validation



\### Nigerian English

\*\*Result:\*\* PASS



Nigerian English speech was successfully recorded, processed and transcribed using:



`NCAIR1/NigerianAccentedEnglish`



The canonical OTP scam scenario was successfully classified as SCAM.



\### Yoruba

\*\*Result:\*\* PASS



Yoruba speech was successfully processed using:



`NCAIR1/Yoruba-ASR`



The resulting transcript contained imperfections but preserved sufficient meaning for the financial-safety journey to be identified.



\### Hausa

\*\*Result:\*\* PASS after stabilization



Hausa speech was successfully processed using:



`NCAIR1/Hausa-ASR`



Development testing revealed that ASR could render `OTP` as forms such as `O.T.P`.



The classifier was therefore hardened to normalize common acronym representations including:



\- OTP

\- O.T.P

\- O.T.P.

\- O T P

\- O-T-P



Equivalent normalization was also introduced for PIN.



After this change, the Hausa OTP scenario correctly routed to SCAM.



\### Igbo

\*\*Result:\*\* PASS



Igbo speech was successfully processed using:



`NCAIR1/Igbo-ASR`



Although the development transcript contained orthographic imperfections, the relevant financial-security meaning and OTP reference were preserved sufficiently for correct SCAM routing.



\---



\## 5. Stabilization Defects Closed



Sprint 2C.1 closed the following identified defects:



\### 5.1 Project `.env` path

The configuration previously resolved `.env` one directory above the VoiceBridge project root.



The configuration was corrected so VoiceBridge reads:



`<project-root>/.env`



A regression test now protects this path.



\### 5.2 ASR security-acronym normalization

Common ASR variations of OTP and PIN are normalized before journey classification.



A regression test covers multiple punctuation and spacing variants.



\### 5.3 TERM response encoding

Corrupted punctuation in the development TERM response was removed and replaced with encoding-safe text.



\### 5.4 Duplicate SCAM safety guidance

The primary SCAM response already contained complete credential-sharing and compromise guidance.



The additional SCAM safety suffix was removed to prevent repetitive output while retaining the separate safety layer for journeys where it provides complementary information.



A regression test protects this behaviour.



\### 5.5 Validation eligibility

Validation eligibility was formalized so an interaction qualifies only when all required conditions are satisfied:



1\. interaction source is voice;

2\. N-ATLAS ASR was successfully used;

3\. the interaction is explicitly marked as a real-user interaction; and

4\. the interaction completed successfully.



Developer voice tests do not qualify.



Text tests do not qualify.



Voice interactions without N-ATLAS ASR do not qualify.



Incomplete interactions do not qualify.



This rule is protected by an automated regression test.



\---



\## 6. Automated Test Closure



Final Sprint 2C.1 automated test result:



\*\*13 collected - 13 passed\*\*



Coverage includes:



\- all six financial-literacy journeys;

\- out-of-scope handling;

\- financial-term definitions;

\- sensitive-data redaction;

\- financial-product guardrails;

\- ASR acronym normalization;

\- duplicate SCAM safety prevention;

\- N-ATLAS message construction;

\- runtime safety;

\- four-language ASR registry;

\- WAV preprocessing;

\- project `.env` resolution; and

\- real-user validation eligibility.



The final pytest output is preserved separately as:



`pytest-final.txt`



\---



\## 7. Development Interaction Baseline



At closure, the VoiceBridge database contained:



\- Total interactions: 20

\- Text-test interactions: 10

\- Voice interactions: 10

\- Qualifying documented N-ATLAS real-user voice interactions: 0

\- Validation target: 50

\- Validation progress: 0.0%



\### Language distribution



\- Nigerian English: 14

\- Hausa: 4

\- Igbo: 1

\- Yoruba: 1



\### Journey distribution



\- LOAN: 1

\- OTHER: 7

\- SAVE: 1

\- SCAM: 9

\- SME: 1

\- TERM: 1



The historical OTHER results are retained as genuine development evidence rather than rewritten or deleted.



They include experiments and earlier routing failures that contributed to subsequent stabilization work.



\---



\## 8. Validation Integrity



All voice interactions completed during Sprint 2C/Sprint 2C.1 were development tests.



They are intentionally marked as non-qualifying and contribute:



\*\*0 interactions\*\*



toward the real-user validation target.



This creates a clean baseline before formal real-user validation begins.



\---



\## 9. Evidence Files



The Sprint 2C.1 evidence directory contains:



\- `SPRINT-2C1-CLOSURE.md`

\- `pytest-final.txt`

\- `asr-diagnostics.json`

\- `interaction-summary.json`



Additional screenshots and selected four-language test evidence may be added to the evidence package separately.



\---



\## 10. Known Limitations at Closure



Sprint 2C.1 closes the ASR stabilization phase but does not imply that the complete VoiceBridge MVP is finished.



Known remaining work includes:



\- genuine N-ATLAS multilingual intelligence integration;

\- replacement of development STUB responses;

\- response-language validation for Nigerian English, Yoruba, Hausa and Igbo;

\- production/cloud deployment decisions;

\- clarification of the NAIC/NCAIR interpretation of "official N-ATLAS ASR service";

\- formal real-user validation;

\- collection of at least 50 qualifying interactions;

\- usability and low-bandwidth testing;

\- competition demo preparation; and

\- final technical documentation.



\---



\## 11. Sprint Closure Decision



\*\*Sprint 2C.1 - Stabilization and Evidence Lock: PASS\*\*



The codebase has reached a stable baseline for the current phase.



Four target ASR language paths have been exercised end-to-end.



Identified stabilization defects have been corrected.



Automated regression coverage has increased to 13 tests, all passing.



Development interactions remain correctly excluded from real-user validation.



The project may now proceed to:



\# Sprint 2D - N-ATLAS Multilingual Intelligence Integration



The Sprint 2C.1 baseline should be preserved before Sprint 2D changes are introduced.

