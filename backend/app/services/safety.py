import re


CARDLIKE = re.compile(r"(?<!\d)(?:\d[ -]*?){12,19}(?!\d)")
BVNLIKE = re.compile(r"(?<!\d)\d{11}(?!\d)")


DANGEROUS_REQUESTS = [
    "guaranteed return",
    "double my money",
    "best investment to buy",
    "which loan should i take",
]


def redact(text: str) -> str:
    """Redact likely sensitive financial identifiers before processing."""
    text = CARDLIKE.sub("[REDACTED NUMBER]", text)
    text = BVNLIKE.sub("[REDACTED IDENTIFIER]", text)
    return text


def precheck(text: str) -> str | None:
    """
    Block requests that would require VoiceBridge to recommend
    a specific financial product or promise financial returns.
    """
    t = text.lower()

    if any(request in t for request in DANGEROUS_REQUESTS):
        return (
            "I can explain financial concepts and risks, but I cannot promise "
            "returns or choose a specific financial product for you. I can help "
            "you compare factors such as cost, risk, fees, repayment terms and "
            "your own objectives."
        )

    return None


def safety_suffix(journey: str) -> str:
    """
    Add only complementary safety guidance.

    SCAM responses already contain the complete credential-sharing
    and compromise guidance, so no additional suffix is required.
    """
    if journey == "SAFE":
        return (
            "\n\nIf you notice activity you do not recognise, report it promptly "
            "through your financial institution's official channel."
        )

    if journey == "LOAN":
        return (
            "\n\nThis is general financial education, not a recommendation "
            "to take a particular loan."
        )

    return ""