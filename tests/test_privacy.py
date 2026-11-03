"""PII redaction tests: the checklist covers phone, SSN, CARD, EMAIL."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from local_model_agents.privacy import Redactor

R = Redactor()


def test_email_redacted():
    out = R.redact("contact jane.doe@example.com for details")
    assert "jane.doe@example.com" not in out.text
    assert out.counts["email"] == 1
    assert "[REDACTED-EMAIL]" in out.text


def test_card_number_redacted():
    # 4111... is a standard test card number (passes Luhn); fictional data.
    out = R.redact("charge card 4111111111111111 please")
    assert "4111111111111111" not in out.text
    assert out.counts["card"] == 1
    assert "[REDACTED-CARD]" in out.text


def test_card_with_spaces_redacted():
    out = R.redact("charge card 4111 1111 1111 1111 please")
    assert "4111" not in out.text
    assert out.counts["card"] == 1


def test_phone_redacted():
    out = R.redact("call me at 555-123-4567 tomorrow")
    assert "555-123-4567" not in out.text
    assert out.counts["phone"] == 1


def test_ssn_redacted():
    out = R.redact("ssn 123-45-6789 on file")
    assert "123-45-6789" not in out.text
    assert out.counts["ssn"] == 1


def test_all_four_types_in_one_text():
    text = (
        "email jane.doe@example.com, card 4111111111111111, "
        "phone 555-123-4567, ssn 123-45-6789"
    )
    out = R.redact(text)
    assert set(out.counts) == {"email", "card", "phone", "ssn"}
    for token in ("jane.doe@example.com", "4111111111111111", "555-123-4567", "123-45-6789"):
        assert token not in out.text


def test_clean_text_unchanged():
    text = "summarize the weekly status notes for the field team"
    out = R.redact(text)
    assert out.text == text
    assert out.counts == {}


def test_non_luhn_digit_string_not_flagged_as_card():
    out = R.redact("reference number 1234567890123456 for the order")
    assert out.counts.get("card", 0) == 0
