# Architecture decision records

## ADR-1: Simulated inference instead of real weights

Decision: the local model is a deterministic keyword-rule stand-in.

Reason: the suite must run fully offline with no downloads, and the
project's subject is agent behaviour around a model (routing,
fallback, gates, audit, measurement), not model quality. A stand-in
keeps every claim in the README provable by the test run.

Consequence: no answer-quality claims are made. Swapping in a real
local runtime is planned work, with the `simulated` flag as the
honesty mechanism.

## ADR-2: Standard library only

Decision: no third-party dependencies.

Reason: zero-install runs anywhere with system Python 3, and there is
nothing to download, which is the whole point of an offline stack.

## ADR-3: Egress ledger stays empty even for comparisons

Decision: a cloud-pattern comparison is simulated locally and records
no egress entry.

Reason: "nothing leaves the device" must be a measurable property of
every mode, not just of local mode. If a real comparison call is ever
added, it must append to the ledger and the privacy claim must change
with it.
