import hashlib
import hmac
import time

from app.config import settings


TOKEN_LIFETIME_SECONDS = 600


def _secret() -> bytes:
    secret = settings.speech_token_secret

    if len(secret) < 48:
        raise RuntimeError(
            "SPEECH_TOKEN_SECRET must contain at least 48 characters"
        )

    return secret.encode("utf-8")


def create_speech_token(interaction_id: str) -> str:
    expires_at = int(time.time()) + TOKEN_LIFETIME_SECONDS

    message = f"{interaction_id}:{expires_at}"

    signature = hmac.new(
        _secret(),
        message.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()

    return f"{expires_at}.{signature}"


def verify_speech_token(
    interaction_id: str,
    token: str,
) -> bool:
    try:
        expires_text, supplied_signature = token.split(".", 1)
        expires_at = int(expires_text)

        if expires_at < int(time.time()):
            return False

        if expires_at > int(time.time()) + TOKEN_LIFETIME_SECONDS:
            return False

        message = f"{interaction_id}:{expires_at}"

        expected_signature = hmac.new(
            _secret(),
            message.encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()

        return hmac.compare_digest(
            expected_signature,
            supplied_signature,
        )

    except (ValueError, AttributeError):
        return False