"""Hash-chained audit tests, including tamper detection."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from local_model_agents.audit import AuditLog


def test_chain_verifies_after_appends():
    log = AuditLog()
    log.append("redacted", "pipeline", {"counts": {"email": 1}})
    log.append("routed", "pipeline", {"destination": "local"})
    log.append("inferred", "pipeline", {"confidence": 0.88})
    assert log.verify() is True


def test_empty_chain_verifies():
    assert AuditLog().verify() is True


def test_tampered_entry_breaks_verification():
    log = AuditLog()
    log.append("redacted", "pipeline", {})
    log.append("routed", "pipeline", {})
    log.entries[0].event = "forged"
    assert log.verify() is False


def test_genesis_entry_links_to_genesis_marker():
    log = AuditLog()
    first = log.append("started", "pipeline", {})
    assert first.prev_hash == "GENESIS"
    assert first.index == 0
