"""SIMULATED local inference.

This is a deterministic stand-in for a local open model. It loads no
weights, downloads nothing, and makes no network call: responses are
produced by fixed keyword rules over the (already redacted) task text,
so the same input always yields the same output and confidence.
Confidence is deliberately low for inputs that match no rule, which is
what drives the fallback path. The ``simulated`` flag is always True
and is surfaced in every result so a simulated answer can never be
mistaken for a real model output.
"""

from __future__ import annotations

from dataclasses import dataclass

MODEL_ID = "simulated-local-standin-v1"

_RULES = (
    ("summarize", 0.88, "Summary: {task}"),
    ("classify", 0.88, "Classification: routine request -- {task}"),
    ("urgent", 0.88, "Classification: urgent request -- {task}"),
    ("ticket", 0.88, "Classification: support ticket -- {task}"),
    ("draft", 0.85, "Draft: {task}"),
    ("explain", 0.85, "Explanation: {task}"),
)


@dataclass(frozen=True)
class InferenceResult:
    text: str
    confidence: float
    model_id: str = MODEL_ID
    simulated: bool = True
    tokens_estimate: int = 0


class SimulatedLocalModel:
    """Deterministic stand-in for a locally run open model."""

    def respond(self, task: str) -> InferenceResult:
        lowered = task.lower()
        for keyword, confidence, template in _RULES:
            if keyword in lowered:
                return InferenceResult(
                    text=template.format(task=task.strip()),
                    confidence=confidence,
                    tokens_estimate=max(1, len(task.split())),
                )
        return InferenceResult(
            text="Insufficient local signal to answer confidently.",
            confidence=0.35,
            tokens_estimate=max(1, len(task.split())),
        )
