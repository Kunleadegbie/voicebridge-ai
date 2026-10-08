import re
import unicodedata


RULES = [
    (
        "SCAM",
        [
            r"\botp\b",
            r"scam",
            r"fraud",
            r"impersonat",
            r"someone called",
            r"bank called",
            r"transfer.*urgent",
        ],
    ),
    (
        "SAFE",
        [
            r"password",
            r"\bpin\b",
            r"suspicious link",
            r"phishing",
            r"hacked",
            r"unauthori[sz]ed",
            r"digital bank",
        ],
    ),
    (
        "LOAN",
        [
            r"loan",
            r"borrow",
            r"interest",
            r"repay",
            r"repayment",
            r"debt",
            r"principal",
        ],
    ),
    (
        "SAVE",
        [
            r"saving",
            r"save money",
            r"savings",
            r"budget",
            r"emergency fund",

            # Yoruba savings expressions
            r"fi\s+owo\s+pamo",
            r"fifi\s+owo\s+pamo",
            r"owo\s+pamo",
            r"fipamo",

            # Hausa savings expressions
            r"ajiye\s+kudi",
            r"ajiyar\s+kudi",
            r"tara\s+kudi",
            r"\bajiy[ae]\b",
            r"\bjiya\s+ku[dr]i\b",

            # Igbo savings expressions
            r"ichekwa\s+ego",
            r"chekwaa\s+ego",
        ],
    ),
    (
        "SME",
        [
            r"business money",
            r"shop money",
            r"cash ?flow",
            r"personal money",
            r"record keeping",
            r"business account",
            r"profit",
        ],
    ),
    (
        "TERM",
        [
            r"what does",
            r"what is",
            r"meaning of",
            r"collateral",
            r"credit score",
            r"inflation",
            r"insurance",
            r"compound interest",
        ],
    ),
]


def classify_journey(text: str) -> str:
    """
    Classify a user's question into one of the six
    VoiceBridge financial-literacy journeys.
    """

    # Normalize accented and unaccented ASR output for matching.
    t = unicodedata.normalize("NFKD", text.lower().strip())
    t = "".join(
        char for char in t
        if not unicodedata.combining(char)
    )

    # Normalize common ASR renderings of security acronyms.
    # Examples:
    # O.T.P / O T P / O-T-P -> otp
    # P.I.N / P I N / P-I-N -> pin
    t = re.sub(r"\bo[\s.\-_]*t[\s.\-_]*p\b", "otp", t)
    t = re.sub(r"\bp[\s.\-_]*i[\s.\-_]*n\b", "pin", t)

    scores = []

    for code, patterns in RULES:
        score = sum(bool(re.search(pattern, t)) for pattern in patterns)

        if score:
            scores.append((score, code))

    return max(scores, default=(0, "OTHER"))[1]


STUB_RESPONSES = {
    "SCAM": (
        "No. Never share an OTP, PIN or password with anyone. "
        "End the conversation and contact your financial institution "
        "through an official channel. If you already shared a credential, "
        "contact the institution immediately and secure the affected account."
    ),

    "SAFE": (
        "Protect the account first. Do not enter credentials through a "
        "suspicious link. Use the institution's official app, website or "
        "published contact channel, change exposed credentials where "
        "appropriate, and report suspicious activity promptly."
    ),

    "LOAN": (
        "Before taking a loan, compare the total amount you will repay with "
        "the amount you receive. Check the interest, fees, repayment dates "
        "and consequences of late payment. Borrow only where the repayment "
        "fits your realistic cash flow."
    ),

    "SAVE": (
        "Start with an amount you can repeat consistently. Separate savings "
        "from everyday spending, set a clear purpose, and automate or schedule "
        "the transfer where possible. For irregular income, consider saving "
        "a percentage whenever income arrives."
    ),

    "SME": (
        "Keep business money separate from personal money. Record money "
        "coming in and going out, review cash flow regularly, and pay "
        "yourself deliberately rather than taking money from the business "
        "without a record. This makes profit and cash needs easier to understand."
    ),

    "TERM": (
        "I can explain financial terms in plain language. Ask the term "
        "directly - for example, 'What does collateral mean?' - and I will "
        "explain what it means and give a simple example."
    ),

    "OTHER": (
        "I can help with basic financial literacy: loans and interest, scams, "
        "savings, digital banking safety, small-business money and everyday "
        "financial terms. Please ask a question in one of those areas."
    ),
}


def stub_response(journey: str, text: str) -> str:
    """
    Return a safe development response for the classified journey.

    This remains a development stub until the N-ATLAS LLM
    is enabled.
    """

    t = text.lower()

    if journey == "TERM":
        definitions = {
            "collateral": (
                "Collateral is an asset a borrower pledges to support a loan. "
                "If the borrower does not repay according to the agreement, "
                "the lender may have rights over that asset. Example: property "
                "may sometimes be used as collateral for a loan."
            ),

            "credit score": (
                "A credit score is a number used to summarise aspects of a "
                "person's credit history and repayment behaviour. Lenders may "
                "use it with other information when assessing credit risk."
            ),

            "inflation": (
                "Inflation means the general level of prices is rising over "
                "time, so the same amount of money may buy fewer goods and "
                "services than before."
            ),

            "insurance": (
                "Insurance is an arrangement where you pay a premium for "
                "financial protection against specified risks, subject to "
                "the terms and exclusions of the policy."
            ),
        }

        for key, value in definitions.items():
            if key in t:
                return value

    return STUB_RESPONSES[journey]