from __future__ import annotations

import io
import wave
from dataclasses import dataclass

import numpy as np

TARGET_SAMPLE_RATE = 16000
MAX_SECONDS = 30.0

class AudioPreprocessError(RuntimeError):
    pass

@dataclass
class PreparedAudio:
    samples: np.ndarray
    sample_rate: int
    duration_ms: int
    channels: int
    source_format: str


def _wav_from_bytes(raw: bytes) -> tuple[np.ndarray, int, int]:
    try:
        with wave.open(io.BytesIO(raw), "rb") as wf:
            channels = wf.getnchannels()
            width = wf.getsampwidth()
            rate = wf.getframerate()
            frames = wf.readframes(wf.getnframes())
    except (wave.Error, EOFError) as exc:
        raise AudioPreprocessError(
            "VoiceBridge Sprint 2C expects browser-recorded WAV audio. Refresh the page and record again."
        ) from exc
    if width != 2:
        raise AudioPreprocessError("Only 16-bit PCM WAV is supported by the Sprint 2C browser recorder.")
    pcm = np.frombuffer(frames, dtype="<i2").astype(np.float32) / 32768.0
    if channels > 1:
        pcm = pcm.reshape(-1, channels).mean(axis=1)
    return pcm, rate, channels


def _resample_linear(samples: np.ndarray, source_rate: int, target_rate: int) -> np.ndarray:
    if source_rate == target_rate or len(samples) == 0:
        return samples.astype(np.float32, copy=False)
    new_len = int(round(len(samples) * target_rate / source_rate))
    old_x = np.linspace(0.0, 1.0, num=len(samples), endpoint=False)
    new_x = np.linspace(0.0, 1.0, num=new_len, endpoint=False)
    return np.interp(new_x, old_x, samples).astype(np.float32)


def prepare_audio(raw: bytes, filename: str = "voice.wav", content_type: str = "audio/wav") -> PreparedAudio:
    if not raw:
        raise AudioPreprocessError("No audio data was received.")
    samples, source_rate, channels = _wav_from_bytes(raw)
    if source_rate <= 0:
        raise AudioPreprocessError("Invalid audio sample rate.")
    samples = _resample_linear(samples, source_rate, TARGET_SAMPLE_RATE)
    duration = len(samples) / TARGET_SAMPLE_RATE
    if duration < 0.25:
        raise AudioPreprocessError("Recording is too short. Please speak for at least a moment before stopping.")
    if duration > MAX_SECONDS:
        raise AudioPreprocessError("Recording exceeds the 30-second N-ATLAS ASR test limit. Please ask a shorter question.")
    peak = float(np.max(np.abs(samples))) if len(samples) else 0.0
    if peak < 0.002:
        raise AudioPreprocessError("The recording is nearly silent. Check the microphone and try again.")
    return PreparedAudio(
        samples=samples,
        sample_rate=TARGET_SAMPLE_RATE,
        duration_ms=int(duration * 1000),
        channels=1,
        source_format="wav-pcm16",
    )
