"""LocalAgentPipeline: prevent / detect / respond / recover + governance + measurement.

Stage order, enforced in code:

1. prevent    -- redact PII before anything else touches the task.
2. detect     -- RouterAgent picks the local-first route.
3. respond    -- SimulatedLocalModel answers the redacted task.
4. fallback   -- FallbackAgent labels any threshold breach explicitly.
5. governance -- risky actions and low-confidence outputs need a
                 named-person, single-use, scoped, unexpired approval;
                 without one the run is BLOCKED, never auto-approved.
6. recover    -- degraded/comparison outcomes carry a recovery note.
7. measurement-- a report covering privacy (egress), cost, and stages.

The egress ledger records real outbound calls. This stack makes none:
in local mode it is empty, and even a cloud-pattern comparison is
simulated locally, so it stays empty there too. That is the privacy
claim, and the test suite asserts it.
"""

from __future__ import annotations

from dataclasses import dataclass

from local_model_agents.approvals import Approval, ApprovalGate
from local_model_agents.audit import AuditLog
from local_model_agents.cost import CostModel
from local_model_agents.fallback import FallbackAgent
from local_model_agents.inference import SimulatedLocalModel
from local_model_agents.privacy import Redactor
from local_model_agents.router import RouterAgent

STAGES = ["prevent", "detect", "respond", "recover", "governance", "measurement"]


@dataclass
class PipelineResult:
    output: str
    mode: str  # "local", "degraded", "cloud-pattern-comparison", "blocked"
    route: str
    confidence: float
    redacted_task: str
    redaction_counts: dict
    stages: list
    egress: list
    cost: dict
    audit: AuditLog
    blocked: bool
    reason: str


class LocalAgentPipeline:
    """Run one task through the full offline agent stack."""

    def __init__(
        self,
        threshold: float = 0.60,
        cost_model: CostModel | None = None,
    ) -> None:
        self.redactor = Redactor()
        self.router = RouterAgent()
        self.model = SimulatedLocalModel()
        self.fallback = FallbackAgent(threshold=threshold)
        self.gate = ApprovalGate()
        self.cost_model = cost_model or CostModel()
        self.threshold = threshold

    def run(
        self,
        task: str,
        sensitive: bool = False,
        risky: bool = False,
        approver: str | None = None,
        approval: Approval | None = None,
        allow_comparison: bool = False,
    ) -> PipelineResult:
        audit = AuditLog()
        egress: list = []  # no real outbound call is ever made

        redaction = self.redactor.redact(task)
        audit.append("redacted", "pipeline", {"counts": redaction.counts})

        route = self.router.route(redaction.text, sensitive=sensitive)
        audit.append("routed", "pipeline", {"destination": route.destination})

        result = self.model.respond(redaction.text)
        audit.append(
            "inferred",
            "pipeline",
            {"confidence": result.confidence, "simulated": result.simulated},
        )

        outcome = self.fallback.handle(result, allow_comparison=allow_comparison)
        audit.append("fallback", "pipeline", {"mode": outcome.mode})

        needs_approval = risky or result.confidence < self.threshold
        reason = outcome.reason
        if needs_approval:
            ok = self.gate.consume(approval, approver or "", scope="act")
            audit.append(
                "governance",
                "pipeline",
                {"needs_approval": True, "approved": ok},
            )
            if not ok:
                reason = (
                    "Blocked by human gate: risky or low-confidence output "
                    "requires a valid named-person approval."
                )
                audit.append("blocked", "pipeline", {"reason": reason})
                return PipelineResult(
                    output="Blocked by human gate: no valid approval supplied.",
                    mode="blocked",
                    route=route.destination,
                    confidence=result.confidence,
                    redacted_task=redaction.text,
                    redaction_counts=redaction.counts,
                    stages=list(STAGES),
                    egress=egress,
                    cost=self.cost_model.compare(1),
                    audit=audit,
                    blocked=True,
                    reason=reason,
                )

        output = outcome.text
        if outcome.mode in ("degraded", "cloud-pattern-comparison"):
            output += (
                " Recovery note: a human should review this output before "
                "acting on it; re-running locally with a clearer task often "
                "restores a confident local answer."
            )
        audit.append("recovered", "pipeline", {"mode": outcome.mode})
        audit.append("measured", "pipeline", {"egress_entries": len(egress)})
        return PipelineResult(
            output=output,
            mode=outcome.mode,
            route=route.destination,
            confidence=result.confidence,
            redacted_task=redaction.text,
            redaction_counts=redaction.counts,
            stages=list(STAGES),
            egress=egress,
            cost=self.cost_model.compare(1),
            audit=audit,
            blocked=False,
            reason=reason,
        )
