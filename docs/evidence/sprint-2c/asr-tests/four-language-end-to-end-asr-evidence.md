# VoiceBridge AI — Sprint 2C Four-Language ASR Evidence

## Evidence Status
Sprint 2C end-to-end development testing completed successfully across all four target languages.

These were DEVELOPMENT interactions only.
They are not part of the NAIC real-user validation dataset and must not count toward the 50-interaction requirement.

## Nigerian English — PASS
Language code: en-NG
ASR model: NCAIR1/NigerianAccentedEnglish
Journey tested: SCAM

Test scenario:
A caller claimed to be from the user's bank and requested an OTP.

Observed result:
- Speech was successfully transcribed.
- Core meaning was preserved.
- OTP was recognised.
- Journey classified as SCAM.
- Appropriate financial-safety response generated.
- UI provenance showed ASR: NATLAS.
- Development interaction remained TEST ONLY.

Assessment:
Strong end-to-end result.

## Yoruba — PASS WITH TRANSCRIPTION IMPERFECTIONS
Language code: yo-NG
ASR model: NCAIR1/Yoruba-ASR
Journey tested: SCAM

Test scenario:
A caller claimed to work for the user's bank and requested an OTP.

Observed result:
- Yoruba speech was successfully processed.
- Transcript contained imperfections.
- Core security meaning remained usable.
- Journey classified as SCAM.
- UI provenance showed ASR: NATLAS / Yoruba-ASR.
- Development interaction remained TEST ONLY.

Assessment:
End-to-end integration passed. Transcription quality should continue to be evaluated during controlled real-user testing.

## Hausa — PASS AFTER ROUTING NORMALIZATION
Language code: ha-NG
ASR model: NCAIR1/Hausa-ASR
Journey tested: SCAM

Test scenario:
A caller claimed to be from the user's bank and requested an OTP.

Observed result:
- Hausa speech was successfully processed.
- ASR rendered OTP in punctuated form such as O.T.P.
- Initial journey routing did not recognise the punctuated acronym reliably.
- Financial-engine normalization was added for common ASR variants including OTP / O.T.P / O T P / O-T-P.
- Regression tests were added.
- Subsequent Hausa test classified correctly as SCAM.
- UI provenance showed ASR: NATLAS / Hausa-ASR.
- Development interaction remained TEST ONLY.

Assessment:
ASR integration passed. The test also identified and resolved a downstream robustness issue without altering the ASR output.

## Igbo — PASS WITH TRANSCRIPTION IMPERFECTIONS
Language code: ig-NG
ASR model: NCAIR1/Igbo-ASR
Journey tested: SCAM

Test scenario:
A caller claimed to work for the user's bank and requested an OTP.

Observed result:
- Igbo speech was successfully processed.
- Transcript contained orthographic/transcription imperfections.
- Key security meaning and OTP reference were retained.
- Journey classified as SCAM.
- UI provenance showed ASR: NATLAS / Igbo-ASR.
- Development interaction remained TEST ONLY.

Assessment:
End-to-end integration passed. Transcription quality should continue to be evaluated during controlled real-user testing.

## Cross-Language Conclusion
Development integration passed across:
- Nigerian English
- Yoruba
- Hausa
- Igbo

Known limitations are deliberately retained in this evidence record rather than hidden.

At Sprint 2C closure:
- N-ATLAS ASR integration: implemented and development-tested.
- N-ATLAS LLM integration: NOT YET ACTIVE.
- Current development response provider: STUB.
- NAIC qualifying real-user validation interactions: 0.
- Development/test interactions must remain excluded from the competition validation count.

## Compliance Qualification
Local mode uses official NCAIR1 Hugging Face ASR repositories.

Whether self-hosting these official repositories satisfies the NAIC wording "official N-ATLAS ASR service", or whether a separately hosted NCAIR/NAIC service is required, remains subject to organizer confirmation.
