"""End-to-end pipeline tests: privacy, gates, fallback, measurement."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from local_model_agents.pipeline import STAGES, LocalAgentPipeline


def _pipe() -> LocalAgentPipeline:
    return LocalAgentPipeline()


def test_local_run_egress_is_empty():
    res = _pipe().run("summarize the weekly status notes")
    assert res.mode == "local"
    assert res.egress == []
    assert res.blocked is False


def test_pii_redacted_before_inference():
    res = _pipe().run(
        "summarize notes for jane.doe@example.com, card 4111111111111111"
    )
    assert "jane.doe@example.com" not in res.redacted_task
    assert "4111111111111111" not in res.redacted_task
    assert res.redaction_counts == {"email": 1, "card": 1}
    assert res.egress == []


def test_low_confidence_without_approval_blocked():
    res = _pipe().run("blorpt zzz unknown task with no matching pattern")
    assert res.blocked is True
    assert res.mode == "blocked"
    assert "human gate" in res.output.lower()


def test_low_confidence_with_approval_degraded():
    pipe = _pipe()
    appr = pipe.gate.grant("priya", "act")
    res = pipe.run(
        "blorpt zzz unknown task with no matching pattern",
        approval=appr,
        approver="priya",
    )
    assert res.blocked is False
    assert res.mode == "degraded"
    assert res.output.startswith("[DEGRADED MODE]")


def test_risky_action_without_approval_blocked():
    res = _pipe().run("summarize the weekly notes", risky=True)
    assert res.blocked is True


def test_risky_action_with_approval_passes():
    pipe = _pipe()
    appr = pipe.gate.grant("priya", "act")
    res = pipe.run("summarize the weekly notes", risky=True, approval=appr, approver="priya")
    assert res.blocked is False
    assert res.mode == "local"


def test_all_six_stages_present():
    res = _pipe().run("summarize the weekly notes")
    assert res.stages == STAGES
    assert set(STAGES) == {
        "prevent", "detect", "respond", "recover", "governance", "measurement",
    }


def test_audit_chain_valid_after_run():
    res = _pipe().run("summarize the weekly notes")
    assert res.audit.verify() is True
    assert len(res.audit.entries) >= 5


def test_measurement_report_includes_cost():
    res = _pipe().run("summarize the weekly notes")
    assert res.cost["local_cheaper"] is True
    assert res.cost["task_count"] == 1
