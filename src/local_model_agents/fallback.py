"""FallbackAgent: explicit fallback, never silent.

When local confidence breaches the threshold, the outcome is one of
two explicit modes, each labelled in the returned text:

* ``degraded`` -- a local degraded answer, prefixed ``[DEGRADED MODE]``.
* ``cloud-pattern-comparison`` -- a simulated comparison against the
  cloud pattern, prefixed ``[CLOUD-PATTERN COMPARISON -- SIMULATED,
  NOT A REAL CLOUD CALL]``. No real cloud call is ever made.

Every outcome carries a reason, so a fallback can never pass
unnoticed in logs, audit entries, or user-facing output.
"""

from __future__ import annotations

from dataclasses import dataclass

from local_model_agents.inference import InferenceResult

DEGRADED_PREFIX = "[DEGRADED MODE]"
COMPARISON_PREFIX = "[CLOUD-PATTERN COMPARISON -- SIMULATED, NOT A REAL CLOUD CALL]"


@dataclass(frozen=True)
class FallbackOutcome:
    mode: str  # "local", "degraded", or "cloud-pattern-comparison"
    text: str
    reason: str


class FallbackAgent:
    """Apply the confidence threshold and label the fallback mode."""

    def __init__(self, threshold: float = 0.60) -> None:
        if not 0.0 <= threshold <= 1.0:
            raise ValueError("threshold must be between 0 and 1")
        self.threshold = threshold

    def handle(
        self, result: InferenceResult, allow_comparison: bool = False
    ) -> FallbackOutcome:
        if result.confidence >= self.threshold:
            return FallbackOutcome(
                mode="local",
                text=result.text,
                reason=f"Confidence {result.confidence} meets threshold {self.threshold}.",
            )
        if allow_comparison:
            return FallbackOutcome(
                mode="cloud-pattern-comparison",
                text=(
                    f"{COMPARISON_PREFIX} Local confidence "
                    f"{result.confidence} breached threshold {self.threshold}; "
                    "a cloud-pattern answer would be compared here, not silently used."
                ),
                reason="Confidence threshold breach with comparison allowed.",
            )
        return FallbackOutcome(
            mode="degraded",
            text=(
                f"{DEGRADED_PREFIX} Local confidence {result.confidence} "
                f"breached threshold {self.threshold}; returning a partial "
                "answer and requesting human review."
            ),
            reason="Confidence threshold breach; degraded local mode.",
        )
