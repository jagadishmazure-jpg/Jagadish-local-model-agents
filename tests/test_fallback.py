"""Fallback tests: threshold breach is explicit, labelled, never silent."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from local_model_agents.fallback import (
    COMPARISON_PREFIX,
    DEGRADED_PREFIX,
    FallbackAgent,
)
from local_model_agents.inference import InferenceResult

F = FallbackAgent(threshold=0.60)


def _res(conf: float) -> InferenceResult:
    return InferenceResult(text="answer", confidence=conf)


def test_above_threshold_stays_local():
    out = F.handle(_res(0.88))
    assert out.mode == "local"
    assert out.text == "answer"


def test_threshold_boundary_stays_local():
    assert F.handle(_res(0.60)).mode == "local"


def test_below_threshold_degraded_by_default():
    out = F.handle(_res(0.35))
    assert out.mode == "degraded"
    assert out.text.startswith(DEGRADED_PREFIX)
    assert out.reason.strip() != ""


def test_below_threshold_comparison_when_allowed():
    out = F.handle(_res(0.35), allow_comparison=True)
    assert out.mode == "cloud-pattern-comparison"
    assert out.text.startswith(COMPARISON_PREFIX)
    assert "NOT A REAL CLOUD CALL" in out.text


def test_fallback_never_silent():
    # Every fallback outcome carries a non-empty reason and a label.
    for out in (F.handle(_res(0.35)), F.handle(_res(0.35), allow_comparison=True)):
        assert out.reason.strip() != ""
        assert out.mode != "local"


def test_invalid_threshold_rejected():
    try:
        FallbackAgent(threshold=1.5)
    except ValueError:
        return
    raise AssertionError("out-of-range threshold should raise")
