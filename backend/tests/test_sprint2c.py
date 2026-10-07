import io, wave
import numpy as np
from app.services.asr_registry import canonical_language, model_for
from app.services.audio import prepare_audio

def _wav(seconds=.5, rate=16000):
    t=np.arange(int(seconds*rate))/rate
    x=(0.05*np.sin(2*np.pi*440*t)*32767).astype('<i2')
    b=io.BytesIO()
    with wave.open(b,'wb') as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(rate); w.writeframes(x.tobytes())
    return b.getvalue()

def test_registry():
    assert model_for('en-NG')['model_id']=='NCAIR1/NigerianAccentedEnglish'
    assert model_for('yo-NG')['model_id']=='NCAIR1/Yoruba-ASR'
    assert canonical_language('Hausa')=='ha-NG'

def test_wav_preprocess():
    p=prepare_audio(_wav(), 'x.wav','audio/wav')
    assert p.sample_rate==16000 and 400 <= p.duration_ms <= 600

def test_project_env_path_is_correct():
    """VoiceBridge settings must read .env from the project root."""
    from pathlib import Path
    from app.config import BASE_DIR

    expected_project_root = Path(__file__).resolve().parents[2]

    assert BASE_DIR == expected_project_root
    assert (BASE_DIR / ".env").exists()


def test_validation_eligibility_rule():
    """Only completed real-user N-ATLAS voice interactions may count."""
    from app.api.voice import is_validation_eligible

    # Qualifying real-user interaction.
    assert is_validation_eligible(
        source="voice",
        natlas_asr=True,
        real_user=True,
        completed=True,
    ) is True

    # Developer voice test must never count.
    assert is_validation_eligible(
        source="voice",
        natlas_asr=True,
        real_user=False,
        completed=True,
    ) is False

    # Text tests must never count.
    assert is_validation_eligible(
        source="text_test",
        natlas_asr=False,
        real_user=True,
        completed=True,
    ) is False

    # Voice without N-ATLAS ASR must never count.
    assert is_validation_eligible(
        source="voice",
        natlas_asr=False,
        real_user=True,
        completed=True,
    ) is False

    # Incomplete interactions must never count.
    assert is_validation_eligible(
        source="voice",
        natlas_asr=True,
        real_user=True,
        completed=False,
    ) is False


