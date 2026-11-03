# Threat model

## Assets

- Task text, which may contain PII (email, card numbers, phone, SSN).
- The audit trail, which must show what the agents did.
- The approval gate, which is the only path to risky actions.

## Threats and mitigations

| Threat | Mitigation | Test |
| --- | --- | --- |
| PII reaches a model or leaves the device | Redaction is stage one, before routing and inference; egress ledger asserted empty | `test_privacy.py`, `test_pipeline.py` |
| Silent fallback to a weaker or external answer | Fallback modes are labelled in the text and carry a reason | `test_fallback.py` |
| Risky action without human approval | Gate blocks on bypass, denial, expiry, reuse, wrong person, wrong scope | `test_approvals.py`, `test_pipeline.py` |
| Contradictory consent treated as approval | Consent with both yes and no language parses as ambiguous | `test_approvals.py` |
| Audit history quietly edited | Hash chain; tampering breaks verification | `test_audit.py` |
| Real company implied as client or endorser | Blocklist stored as hashes only; scan asserted over repo materials | `test_brand_offline.py` |
| Simulated output mistaken for a real model | Every result carries `simulated=True` and a stand-in model id | `test_inference.py` |

## Known gaps (kept visible)

- The inference stand-in is rule-based, so its "confidence" is a
  routing signal, not a calibrated probability. A real local runtime
  must supply calibrated confidence before the threshold is trusted
  for anything beyond demonstration.
- Redaction is pattern-based; adversarially formatted PII can evade
  patterns. Treat redaction as a safety layer, not a guarantee.
- Cost parameters are illustrative, not vendor prices, and are
  labelled as such wherever they appear.
