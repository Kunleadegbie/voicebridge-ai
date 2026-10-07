from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parents[2]

class Settings(BaseSettings):
    app_name: str = "VoiceBridge AI"
    environment: str = "development"
    database_url: str = "sqlite:///./voicebridge.db"

    # Official N-ATLAS ASR. Keep pending until NCAIR provides the documented interface.
    natlas_asr_mode: str = "pending"  # pending | local | api
    natlas_asr_url: str = ""
    natlas_asr_api_key: str = ""
    natlas_asr_device: str = "auto"  # auto | cpu
    natlas_asr_timeout_seconds: int = 120

    # N-ATLAS LLM: stub for development; api is preferred for competition deployment;
    # local is available for a sufficiently capable machine.
    natlas_llm_mode: str = "stub"     # stub | api | local
    natlas_llm_url: str = ""
    natlas_llm_api_key: str = ""
    natlas_model_name: str = "NCAIR1/N-ATLaS"
    natlas_hf_token: str = ""
    natlas_local_device: str = "auto" # auto | cuda | cpu
    natlas_local_dtype: str = "auto"  # auto | float16 | bfloat16 | float32
    natlas_max_new_tokens: int = 280
    natlas_temperature: float = 0.1
    natlas_request_timeout_seconds: int = 120

    max_audio_mb: int = 12
    model_config = SettingsConfigDict(env_file=BASE_DIR / ".env", extra="ignore")

settings = Settings()
