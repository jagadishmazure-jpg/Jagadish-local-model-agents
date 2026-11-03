# Local-model agents: distilled notes

Original notes written for this project. The fictional company used
throughout is **Vexmere Edge**, a made-up field-services firm. No real
company, client, or vendor-as-client appears anywhere in this repo.

## The problem in one paragraph

Running agents on a remote model sends task text off the device, costs
money per call, and fails when the network does. Running agents on a
local model keeps data on the device and removes the per-call charge,
but a small local model is weaker: it will sometimes answer with low
confidence, and it cannot know live facts. A useful local stack therefore
needs more than a model -- it needs routing that prefers local, a
fallback that says so out loud when confidence drops, redaction before
anything is processed, a human gate for risky or uncertain actions, an
audit trail that cannot be quietly edited, and measurement that proves
the privacy and cost claims instead of asserting them.

## Design decisions

- **Local-first routing.** Every task starts local. Only a task that
  explicitly asks for live external data is labelled for a cloud-pattern
  comparison, and sensitive or redacted content never takes that route.
- **Explicit fallback, never silent.** A confidence breach produces a
  degraded local answer or a clearly labelled simulated comparison.
  Both carry a reason, and both carry a recovery note asking for human
  review. Silence is treated as a bug.
- **Redact first.** PII redaction is stage one, before routing and
  inference. The checklist covers phone numbers, SSNs, card numbers,
  and email addresses. Card candidates must pass a Luhn check so
  ordinary long digit strings are not misclassified.
- **Human gates with teeth.** Approvals are named-person, single-use,
  scoped, and expiring. Bypass (no approval), rejection, expiry, reuse,
  wrong person, and wrong scope all block. Free-text consent that
  contradicts itself ("yes, wait, no") is ambiguous and never approval.
- **Hash-chained audit.** Each entry hashes the previous one, so
  editing history breaks verification of everything after the edit.
- **Measurement as a feature.** Privacy is measured as an egress
  ledger (empty in every mode, because even the comparison is
  simulated locally). Cost is measured as a local-vs-cloud-pattern
  comparison on the same task set, with local cheaper by construction
  of the model parameters, which are labelled illustrative, not vendor
  prices.

## What is simulated, stated plainly

The inference component is a deterministic keyword-rule stand-in. It
loads no weights, downloads no model, and makes no network call. That
is intentional: it makes the suite runnable fully offline and keeps
the focus on agent behaviour -- routing, fallback, gates, audit, and
measurement -- which is what the tests assert. Swapping the stand-in
for a real local runtime is a planned step, not a built one.
