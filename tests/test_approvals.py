"""Approval-gate tests: bypass, reject, absent, reuse, expiry, scope,
person, low-confidence gating, and self-contradicting consent."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from local_model_agents.approvals import ApprovalGate, parse_consent


def test_grant_and_consume_once():
    gate = ApprovalGate()
    appr = gate.grant("priya", "act")
    assert gate.consume(appr, "priya", "act") is True


def test_single_use_reuse_rejected():
    gate = ApprovalGate()
    appr = gate.grant("priya", "act")
    assert gate.consume(appr, "priya", "act") is True
    assert gate.consume(appr, "priya", "act") is False


def test_absent_approval_rejected():
    gate = ApprovalGate()
    assert gate.consume(None, "priya", "act") is False


def test_denied_approval_rejected():
    gate = ApprovalGate()
    appr = gate.grant("priya", "act")
    gate.deny(appr)
    assert gate.consume(appr, "priya", "act") is False


def test_expired_approval_rejected():
    gate = ApprovalGate()
    appr = gate.grant("priya", "act", ttl_seconds=-10)
    assert gate.consume(appr, "priya", "act") is False


def test_wrong_person_rejected():
    gate = ApprovalGate()
    appr = gate.grant("priya", "act")
    assert gate.consume(appr, "ravi", "act") is False


def test_wrong_scope_rejected():
    gate = ApprovalGate()
    appr = gate.grant("priya", "act")
    assert gate.consume(appr, "priya", "delete") is False


def test_anonymous_grant_rejected():
    gate = ApprovalGate()
    try:
        gate.grant("", "act")
    except ValueError:
        return
    raise AssertionError("anonymous grant should raise")


def test_self_contradicting_consent_is_ambiguous():
    assert parse_consent("yes, wait, no") == "ambiguous"
    assert parse_consent("yes but hold on, no") == "ambiguous"


def test_plain_consent_parses():
    assert parse_consent("yes, go ahead") == "approved"
    assert parse_consent("no, stop") == "denied"
    assert parse_consent("maybe later") == "ambiguous"
