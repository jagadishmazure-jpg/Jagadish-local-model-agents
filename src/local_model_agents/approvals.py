"""Named-person, single-use, scoped, expiring approvals.

An approval is granted to one named person, for one scope, with a
time-to-live. Consuming it checks all four properties; a second use,
the wrong person, the wrong scope, or an expired approval all fail.

Consent language is parsed conservatively: text that contains both an
affirmation and a negation -- for example "yes, wait, no" -- is
AMBIGUOUS and never counts as approval. Low-confidence results always
require an approval before their output may be acted on.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone


@dataclass
class Approval:
    token: str
    approver: str
    scope: str
    expires_at: datetime
    used: bool = False
    denied: bool = False


class ApprovalGate:
    """Issue and consume single-use, expiring, scoped approvals."""

    def __init__(self) -> None:
        self._approvals: dict = {}
        self._counter = 0

    def grant(self, approver: str, scope: str, ttl_seconds: int = 300) -> Approval:
        if not approver or not approver.strip():
            raise ValueError("approver must be a named person")
        if not scope or not scope.strip():
            raise ValueError("scope must be non-empty")
        self._counter += 1
        approval = Approval(
            token=f"appr-{self._counter}",
            approver=approver.strip(),
            scope=scope.strip(),
            expires_at=datetime.now(timezone.utc) + timedelta(seconds=ttl_seconds),
        )
        self._approvals[approval.token] = approval
        return approval

    def deny(self, approval: Approval) -> None:
        approval.denied = True

    def consume(self, approval: Approval | None, approver: str, scope: str) -> bool:
        """Return True only if the approval is valid for this use.

        Bypass (no approval), reject (denied), wrong person, wrong
        scope, reuse, and expiry all return False.
        """
        if approval is None:
            return False
        if approval.denied or approval.used:
            return False
        if approval.approver != approver or approval.scope != scope:
            return False
        if datetime.now(timezone.utc) > approval.expires_at:
            return False
        approval.used = True
        return True


_YES = re.compile(r"\b(yes|approve|approved|go ahead|confirm)\b", re.I)
_NO = re.compile(r"\b(no|deny|denied|stop|wait|cancel|hold on)\b", re.I)


def parse_consent(text: str) -> str:
    """Parse free-text consent into approved / denied / ambiguous.

    Any text containing both affirming and negating language is
    ambiguous, including self-contradicting consent such as
    "yes, wait, no". Ambiguous is never approval.
    """
    yes = bool(_YES.search(text))
    no = bool(_NO.search(text))
    if yes and no:
        return "ambiguous"
    if yes:
        return "approved"
    if no:
        return "denied"
    return "ambiguous"
