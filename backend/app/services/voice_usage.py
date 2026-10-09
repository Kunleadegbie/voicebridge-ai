import sqlite3

from contextlib import closing
from datetime import datetime, timezone
from pathlib import Path


DB_PATH = Path(__file__).resolve().parents[2] / "speech_usage.db"

VOICE_HOURLY_LIMIT = 10
VOICE_DAILY_LIMIT = 30


class VoiceLimitExceeded(Exception):
    """Raised when the voice request allowance is exhausted."""
    pass


def reserve_voice_request() -> None:
    """
    Reserve one voice request before running ASR or LLM.

    Reservations are counted even when processing fails.
    Limits apply across the entire demonstration.
    """

    now = datetime.now(timezone.utc)

    hour_key = now.strftime("%Y-%m-%dT%H")
    day_key = now.strftime("%Y-%m-%d")

    with closing(sqlite3.connect(DB_PATH, timeout=10)) as connection:
        with connection:
            connection.execute("BEGIN IMMEDIATE")

            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS voice_usage (
                    period_type TEXT NOT NULL,
                    period_key TEXT NOT NULL,
                    request_count INTEGER NOT NULL DEFAULT 0,
                    PRIMARY KEY (period_type, period_key)
                )
                """
            )

            hour_row = connection.execute(
                """
                SELECT request_count
                FROM voice_usage
                WHERE period_type = 'hour'
                  AND period_key = ?
                """,
                (hour_key,),
            ).fetchone()

            day_row = connection.execute(
                """
                SELECT request_count
                FROM voice_usage
                WHERE period_type = 'day'
                  AND period_key = ?
                """,
                (day_key,),
            ).fetchone()

            hour_count = hour_row[0] if hour_row else 0
            day_count = day_row[0] if day_row else 0

            if hour_count >= VOICE_HOURLY_LIMIT:
                raise VoiceLimitExceeded(
                    "Hourly voice request limit reached"
                )

            if day_count >= VOICE_DAILY_LIMIT:
                raise VoiceLimitExceeded(
                    "Daily voice request limit reached"
                )

            for period_type, period_key in (
                ("hour", hour_key),
                ("day", day_key),
            ):
                connection.execute(
                    """
                    INSERT INTO voice_usage (
                        period_type,
                        period_key,
                        request_count
                    )
                    VALUES (?, ?, 1)
                    ON CONFLICT(period_type, period_key)
                    DO UPDATE SET
                        request_count = request_count + 1
                    """,
                    (period_type, period_key),
                )