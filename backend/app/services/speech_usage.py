
import sqlite3

from contextlib import closing
from datetime import datetime, timezone
from pathlib import Path

from app.config import settings


# Store speech usage information in the backend directory.
DB_PATH = Path(__file__).resolve().parents[2] / "speech_usage.db"


class SpeechLimitExceeded(Exception):
    """Raised when a speech-generation limit is reached."""
    pass


def reserve_speech_generation() -> None:
    """
    Reserve one new speech generation against the hourly
    and daily server-wide limits.

    Reservations count even if the speech provider later fails.
    This is conservative and helps protect paid credits.

    Cached speech playback does not call this function.
    """

    # Step 1: Determine the current UTC hour and day.
    now = datetime.now(timezone.utc)

    hour_key = now.strftime("%Y-%m-%dT%H")
    day_key = now.strftime("%Y-%m-%d")

    # Step 2: Read the configured generation limits.
    hourly_limit = max(
        0,
        settings.tts_hourly_limit,
    )

    daily_limit = max(
        0,
        settings.tts_daily_limit,
    )

    # Step 3: Open the database with explicit cleanup.
    with closing(
        sqlite3.connect(DB_PATH, timeout=10)
    ) as connection:

        with connection:

            # Lock before reading or updating counters.
            connection.execute("BEGIN IMMEDIATE")

            # Create the tracking table if it does not exist.
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS speech_usage (
                    period_type TEXT NOT NULL,
                    period_key TEXT NOT NULL,
                    request_count INTEGER NOT NULL DEFAULT 0,
                    PRIMARY KEY (period_type, period_key)
                )
                """
            )

            # Step 4: Retrieve the current hourly count.
            hour_row = connection.execute(
                """
                SELECT request_count
                FROM speech_usage
                WHERE period_type = 'hour'
                  AND period_key = ?
                """,
                (hour_key,),
            ).fetchone()

            # Step 5: Retrieve the current daily count.
            day_row = connection.execute(
                """
                SELECT request_count
                FROM speech_usage
                WHERE period_type = 'day'
                  AND period_key = ?
                """,
                (day_key,),
            ).fetchone()

            hour_count = (
                hour_row[0]
                if hour_row is not None
                else 0
            )

            day_count = (
                day_row[0]
                if day_row is not None
                else 0
            )

            # Step 6: Enforce the hourly limit.
            if hour_count >= hourly_limit:
                raise SpeechLimitExceeded(
                    "Hourly speech generation limit reached"
                )

            # Step 7: Enforce the daily limit.
            if day_count >= daily_limit:
                raise SpeechLimitExceeded(
                    "Daily speech generation limit reached"
                )

            # Step 8: Reserve one generation in both counters.
            for period_type, period_key in (
                ("hour", hour_key),
                ("day", day_key),
            ):
                connection.execute(
                    """
                    INSERT INTO speech_usage (
                        period_type,
                        period_key,
                        request_count
                    )
                    VALUES (?, ?, 1)
                    ON CONFLICT(period_type, period_key)
                    DO UPDATE SET
                        request_count = request_count + 1
                    """,
                    (
                        period_type,
                        period_key,
                    ),
                )

        # The transaction has committed successfully.
        # The outer closing() context closes the SQLite
        # connection, including on exceptions.
