# Security policy

This is a portfolio demonstration project. It contains no real user data,
no real credentials, and no real model weights. All example data is
fictional, and the "local model" is a deterministic simulated stand-in.

If you find a genuine security issue in this code (for example, a
redaction bypass or an audit-chain weakness), please report it through
the repository's private vulnerability reporting channel rather than
opening a public issue with exploit details.

## What this project does NOT do

- It never sends task text, redacted or otherwise, to any external
  service. The test suite asserts the egress ledger stays empty.
- It never loads, downloads, or executes real model weights.
- It never auto-approves a risky or low-confidence action; the human
  gate blocks by default.
