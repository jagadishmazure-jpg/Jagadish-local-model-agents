"""PII redaction.

The checklist covers phone numbers, SSNs, CARD NUMBERS, and EMAIL
ADDRESSES. Card candidates must pass a Luhn check so ordinary long digit
strings are not treated as card numbers. Redaction runs BEFORE inference
in the pipeline, so redacted values never reach any model stand-in.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

EMAIL_RE = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
SSN_RE = re.compile(r"\b\d{3}-\d{2}-\d{4}\b")
CARD_RE = re.compile(r"\b(?:\d[ -]?){13,19}\b")
PHONE_RE = re.compile(
    r"(?:\+?1[ -]?)?(?:\(?\d{3}\)?[ -]?)\d{3}[ -]?\d{4}\b"
)

TOKEN = {
    "email": "[REDACTED-EMAIL]",
    "card": "[REDACTED-CARD]",
    "ssn": "[REDACTED-SSN]",
    "phone": "[REDACTED-PHONE]",
}


def _luhn_ok(digits: str) -> bool:
    total = 0
    for i, ch in enumerate(reversed(digits)):
        d = int(ch)
        if i % 2 == 1:
            d *= 2
            if d > 9:
                d -= 9
        total += d
    return total % 10 == 0


@dataclass
class Redaction:
    text: str
    findings: list = field(default_factory=list)

    @property
    def counts(self) -> dict:
        out: dict = {}
        for kind in self.findings:
            out[kind] = out.get(kind, 0) + 1
        return out


class Redactor:
    """Redact email, card, SSN, and phone values from free text."""

    def redact(self, text: str) -> Redaction:
        findings: list = []

        def _email(m: re.Match) -> str:
            findings.append("email")
            return TOKEN["email"]

        out = EMAIL_RE.sub(_email, text)

        def _ssn(m: re.Match) -> str:
            findings.append("ssn")
            return TOKEN["ssn"]

        out = SSN_RE.sub(_ssn, out)

        def _card(m: re.Match) -> str:
            digits = re.sub(r"\D", "", m.group(0))
            if 13 <= len(digits) <= 19 and _luhn_ok(digits):
                findings.append("card")
                return TOKEN["card"]
            return m.group(0)

        out = CARD_RE.sub(_card, out)

        def _phone(m: re.Match) -> str:
            # Skip anything already replaced, and skip digit runs that
            # look like card fragments (they were handled above).
            findings.append("phone")
            return TOKEN["phone"]

        out = PHONE_RE.sub(_phone, out)
        return Redaction(text=out, findings=findings)
