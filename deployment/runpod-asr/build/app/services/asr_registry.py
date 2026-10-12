from __future__ import annotations

MODEL_REGISTRY = {
    "en-NG": {
        "name": "Nigerian English",
        "model_id": "NCAIR1/NigerianAccentedEnglish",
        "hf_language": "en",
    },
    "yo-NG": {
        "name": "Yoruba",
        "model_id": "NCAIR1/Yoruba-ASR",
        "hf_language": "yo",
    },
    "ha-NG": {
        "name": "Hausa",
        "model_id": "NCAIR1/Hausa-ASR",
        "hf_language": "ha",
    },
    "ig-NG": {
        "name": "Igbo",
        "model_id": "NCAIR1/Igbo-ASR",
        "hf_language": "ig",
    },
}

ALIASES = {
    "en": "en-NG", "en-ng": "en-NG", "english": "en-NG", "nigerian english": "en-NG",
    "yo": "yo-NG", "yo-ng": "yo-NG", "yoruba": "yo-NG", "yorùbá": "yo-NG",
    "ha": "ha-NG", "ha-ng": "ha-NG", "hausa": "ha-NG",
    "ig": "ig-NG", "ig-ng": "ig-NG", "igbo": "ig-NG",
}

def canonical_language(value: str) -> str:
    raw = (value or "en-NG").strip()
    if raw in MODEL_REGISTRY:
        return raw
    return ALIASES.get(raw.lower(), "en-NG")

def model_for(language: str) -> dict:
    return MODEL_REGISTRY[canonical_language(language)]
