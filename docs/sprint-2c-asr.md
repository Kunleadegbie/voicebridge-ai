# Sprint 2C — Official N-ATLAS ASR Integration

## Scope
- Official four-language NCAIR1 model registry.
- Lazy local loading and in-process caching.
- Nigerian-English first-test path.
- Browser microphone capture as mono PCM WAV (avoids an FFmpeg dependency for the MVP).
- Audio validation/resampling to 16 kHz.
- Provenance: ASR provider, exact model ID, ASR mode, audio duration and ASR latency.
- `/asr/diagnostics` and `/providers/status` diagnostics.
- Development voice tests default to `real_user=false` and are excluded from NAIC validation counts.

## Registry
- en-NG → NCAIR1/NigerianAccentedEnglish
- yo-NG → NCAIR1/Yoruba-ASR
- ha-NG → NCAIR1/Hausa-ASR
- ig-NG → NCAIR1/Igbo-ASR

## First acceptance test
Speak in Nigerian English:
“Someone called me and said they are from my bank. They asked me to tell them the OTP that came to my phone. Should I give it to them?”

Expected provenance: `source=voice`, `asr_provider=natlas`, exact NigerianAccentedEnglish model ID, `real_user=false`, `validation_eligible=false`.

## Compliance note
Local mode runs the official NCAIR1 N-ATLAS ASR model repositories. The NAIC wording “official N-ATLAS ASR service” should still be confirmed with the organisers before final competition submission; this package does not claim that self-hosting has already been accepted as equivalent to a hosted official service.
