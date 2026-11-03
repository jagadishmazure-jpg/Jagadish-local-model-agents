"""Local-model agent stack: offline-capable agents on local open models.

Everything in this package is a deterministic, standard-library-only
stand-in. The "local model" here is SIMULATED: no weights are loaded, no
model is downloaded, and no network call is made. The value of the stack
is the surrounding agent behaviour -- routing, fallback, redaction,
approval gates, hash-chained audit, and measurement -- which is exactly
what the test suite asserts.
"""

from local_model_agents.privacy import Redactor, Redaction
from local_model_agents.audit import AuditLog
from local_model_agents.approvals import ApprovalGate, parse_consent
from local_model_agents.cost import CostModel
from local_model_agents.inference import SimulatedLocalModel, InferenceResult
from local_model_agents.router import RouterAgent, Route
from local_model_agents.fallback import FallbackAgent, FallbackOutcome
from local_model_agents.pipeline import LocalAgentPipeline, PipelineResult

__all__ = [
    "Redactor",
    "Redaction",
    "AuditLog",
    "ApprovalGate",
    "parse_consent",
    "CostModel",
    "SimulatedLocalModel",
    "InferenceResult",
    "RouterAgent",
    "Route",
    "FallbackAgent",
    "FallbackOutcome",
    "LocalAgentPipeline",
    "PipelineResult",
]
