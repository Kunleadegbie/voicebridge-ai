SUPPORTED = {"en-NG", "yo-NG", "ha-NG", "ig-NG"}

LANGUAGE_NAMES = {
    "en-NG": "Nigerian English",
    "yo-NG": "Yoruba",
    "ha-NG": "Hausa",
    "ig-NG": "Igbo",
}


def normalize_language(value: str) -> str:
    return value if value in SUPPORTED else "en-NG"


def language_name(value: str) -> str:
    """
    Return the canonical human-readable name for a VoiceBridge language.

    Unsupported values safely fall back to Nigerian English,
    consistent with normalize_language().
    """
    normalized = normalize_language(value)
    return LANGUAGE_NAMES[normalized]
