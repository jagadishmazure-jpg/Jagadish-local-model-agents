"""RouterAgent: local-first routing.

Default route is local. A task is routed to a clearly-labelled
cloud-pattern comparison ONLY when it asks for live external data
(e.g. a live price or current conditions) that a local model cannot
know. Sensitive tasks -- flagged sensitive, or containing a redaction
token -- never leave the local route. Routing is deterministic and
explained in the returned reason.
"""

from __future__ import annotations

from dataclasses import dataclass

_EXTERNAL_MARKERS = (
    "live price",
    "current weather",
    "latest news",
    "real-time",
    "stock price today",
)

_REDACTION_TOKENS = ("[REDACTED-",)


@dataclass(frozen=True)
class Route:
    destination: str  # "local" or "cloud-pattern-comparison"
    reason: str


class RouterAgent:
    """Route every task local-first; external-data tasks get a label."""

    def route(self, task: str, sensitive: bool = False) -> Route:
        lowered = task.lower()
        if sensitive or any(tok in task for tok in _REDACTION_TOKENS):
            return Route(
                destination="local",
                reason="Sensitive or redacted content stays local.",
            )
        if any(marker in lowered for marker in _EXTERNAL_MARKERS):
            return Route(
                destination="cloud-pattern-comparison",
                reason="Task asks for live external data; local model cannot know it.",
            )
        return Route(destination="local", reason="Local-first default route.")
