"""Simulated-inference tests: deterministic, labelled simulated."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from local_model_agents.inference import MODEL_ID, SimulatedLocalModel

M = SimulatedLocalModel()


def test_result_always_flagged_simulated():
    res = M.respond("summarize the weekly notes")
    assert res.simulated is True
    assert res.model_id == MODEL_ID
    assert "simulated" in res.model_id


def test_deterministic_repeat():
    a = M.respond("classify this ticket: scanner offline")
    b = M.respond("classify this ticket: scanner offline")
    assert a == b


def test_summarize_rule_high_confidence():
    res = M.respond("summarize the weekly status notes")
    assert res.confidence == 0.88
    assert res.text.startswith("Summary:")


def test_classify_rule_high_confidence():
    res = M.respond("classify this ticket: scanner offline")
    assert res.confidence == 0.88


def test_unknown_input_low_confidence():
    res = M.respond("blorpt zzz unknown task with no matching pattern")
    assert res.confidence == 0.35
    assert res.confidence < 0.60


def test_no_weights_no_download_claim():
    # The stand-in's contract: no model artifact is referenced anywhere.
    assert "weight" not in MODEL_ID
    assert M.respond("draft a reply").simulated is True
