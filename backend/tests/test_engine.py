from app.services.financial_engine import classify_journey, stub_response
from app.services.safety import redact, precheck

def test_all_journeys():
    cases={"SCAM":"They asked me for my OTP","SAFE":"I clicked a suspicious link","LOAN":"How much interest is on this loan?","SAVE":"How can I start saving money?","SME":"Should I separate my shop money from personal money?","TERM":"What does collateral mean?"}
    for expected,text in cases.items(): assert classify_journey(text)==expected

def test_out_of_scope(): assert classify_journey("Tell me the football score") == "OTHER"
def test_term_definition(): assert "asset" in stub_response("TERM","What does collateral mean?")
def test_sensitive_redaction(): assert "12345678901" not in redact("My BVN is 12345678901")
def test_product_guardrail(): assert precheck("Which loan should I take?") is not None

def test_asr_security_acronym_normalization():
    """ASR punctuation/spacing variants of security acronyms must classify safely."""
    otp_variants = [
        "Someone from my bank asked for my OTP",
        "Someone from my bank asked for my O.T.P",
        "Someone from my bank asked for my O.T.P.",
        "Someone from my bank asked for my O T P",
        "Someone from my bank asked for my O-T-P",
        "wani ya kira ni daga banki, ya ce in ba shi o.t.p na",
    ]

    for text in otp_variants:
        assert classify_journey(text) == "SCAM"

    pin_variants = [
        "Someone asked me for my PIN",
        "Someone asked me for my P.I.N",
        "Someone asked me for my P I N",
        "Someone asked me for my P-I-N",
    ]

    for text in pin_variants:
        assert classify_journey(text) == "SAFE"

def test_scam_safety_suffix_does_not_duplicate_response():
    """SCAM response already contains complete safety guidance."""
    from app.services.safety import safety_suffix

    assert safety_suffix("SCAM") == ""


