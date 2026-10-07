import argparse, asyncio
from pathlib import Path
from app.services.natlas_asr import transcribe

p=argparse.ArgumentParser(description="VoiceBridge Sprint 2C Nigerian-English N-ATLAS ASR smoke test")
p.add_argument("wav", help="Path to a 16-bit PCM WAV recording, <=30 seconds")
a=p.parse_args(); raw=Path(a.wav).read_bytes()
r=asyncio.run(transcribe(raw,Path(a.wav).name,"audio/wav","en-NG"))
print("MODEL:",r.model_id); print("MODE:",r.mode); print("AUDIO_MS:",r.duration_ms); print("ASR_MS:",r.asr_latency_ms); print("TRANSCRIPT:",r.transcript)
