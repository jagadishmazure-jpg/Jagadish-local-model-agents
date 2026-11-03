# Implementation guide

## Layout

- `src/local_model_agents/` -- the stack, standard library only.
  - `privacy.py` -- redaction (email, card with Luhn check, SSN, phone).
  - `router.py` -- RouterAgent, local-first routing.
  - `inference.py` -- SimulatedLocalModel, deterministic stand-in.
  - `fallback.py` -- FallbackAgent, threshold + explicit labelled modes.
  - `approvals.py` -- ApprovalGate + conservative consent parsing.
  - `audit.py` -- hash-chained audit log.
  - `cost.py` -- local-vs-cloud-pattern cost comparison.
  - `brand.py` -- SHA-256-hash-only blocklist check.
  - `pipeline.py` -- LocalAgentPipeline, all stages in order.
- `tests/` -- 59 tests, all offline.
- `examples/run_demo.py` -- fixed 6-task demo printing measured numbers.
- `knowledge/` -- distilled notes and the architecture diagram.

## Using the pipeline

```python
from local_model_agents.pipeline import LocalAgentPipeline

pipe = LocalAgentPipeline()
result = pipe.run("summarize the weekly status notes")
print(result.mode)        # "local"
print(result.egress)      # [] -- nothing leaves the device
print(result.audit.verify())  # True
```

A risky or low-confidence run needs an approval, or it is blocked:

```python
pipe = LocalAgentPipeline()
approval = pipe.gate.grant("priya", "act")
result = pipe.run("blorpt zzz unknown task", approval=approval, approver="priya")
print(result.mode)  # "degraded", with a [DEGRADED MODE] label
```

## Swapping in a real local runtime (planned, not built)

Replace `SimulatedLocalModel.respond` with a call to a real local
runtime, keeping the contract: return text plus a confidence value,
keep the `simulated` flag honest (set it False only when a real model
actually ran), and keep redaction and routing in front of it. The
fallback, gate, audit, and measurement stages do not change.

## Running

```sh
python3 -m pytest tests/
python3 examples/run_demo.py
```

No dependencies to install, no model to download, no network needed.
