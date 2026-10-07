from app.services.natlas_llm import _messages
from app.services.runtime import runtime_status

def test_natlas_message_contains_journey_and_language():
    messages = _messages("What is collateral?", "TERM", "en-NG")
    assert messages[0]["role"] == "system"
    assert "TERM" in messages[1]["content"]
    assert "en-NG" in messages[1]["content"]

def test_runtime_status_is_safe_without_local_dependencies():
    status = runtime_status()
    assert "recommended_competition_route" in status
    assert status["recommended_competition_route"] == "official_or_hosted_api"

def test_multilingual_prompt_contract():
    """N-ATLAS prompt must explicitly identify and enforce each response language."""
    from app.services.natlas_llm import _messages

    languages = {
        "en-NG": "Nigerian English",
        "yo-NG": "Yoruba",
        "ha-NG": "Hausa",
        "ig-NG": "Igbo",
    }

    for code, name in languages.items():
        messages = _messages(
            text="Test financial literacy question",
            journey="SCAM",
            language=code,
        )

        user_prompt = messages[1]["content"]

        assert f"Required response language: {name} ({code})" in user_prompt
        assert f"Respond in {name}." in user_prompt


def test_multilingual_prompt_unsupported_language_falls_back_safely():
    """Unsupported language codes must fall back to Nigerian English."""
    from app.services.natlas_llm import _messages

    messages = _messages(
        text="Test question",
        journey="TERM",
        language="xx-XX",
    )

    user_prompt = messages[1]["content"]

    assert "Required response language: Nigerian English (en-NG)" in user_prompt
    assert "Respond in Nigerian English." in user_prompt

def test_llm_generate_stub_provenance():
    """Stub mode must never be reported as genuine N-ATLAS inference."""
    import asyncio
    from unittest.mock import patch

    from app.services.natlas_llm import generate

    async def run_test():
        with patch("app.services.natlas_llm.settings.natlas_llm_mode", "stub"):
            response, natlas_llm = await generate(
                text="Someone asked me for my OTP",
                journey="SCAM",
                language="en-NG",
            )

        assert isinstance(response, str)
        assert response.strip()
        assert natlas_llm is False

    asyncio.run(run_test())


def test_llm_generate_api_provenance():
    """Successful API inference must be reported as genuine N-ATLAS inference."""
    import asyncio
    from unittest.mock import AsyncMock, patch

    from app.services.natlas_llm import generate

    async def run_test():
        with patch("app.services.natlas_llm.settings.natlas_llm_mode", "api"):
            with patch(
                "app.services.natlas_llm._generate_api",
                new=AsyncMock(return_value="N-ATLAS test response"),
            ):
                response, natlas_llm = await generate(
                    text="What does collateral mean?",
                    journey="TERM",
                    language="en-NG",
                )

        assert response == "N-ATLAS test response"
        assert natlas_llm is True

    asyncio.run(run_test())
