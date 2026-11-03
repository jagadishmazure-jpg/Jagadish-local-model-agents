# Architecture

```mermaid
flowchart TD
    Task[User task] --> Prevent[prevent: Redactor\nphone, SSN, card, email]
    Prevent --> Detect[detect: RouterAgent\nlocal-first]
    Detect --> Respond[respond: SimulatedLocalModel\ndeterministic stand-in, no weights]
    Respond --> Fallback[fallback: FallbackAgent\nconfidence threshold]
    Fallback --> Govern[governance: ApprovalGate\nnamed-person, single-use, scoped, expiring]
    Govern --> Recover[recover: recovery note\non degraded / comparison outcomes]
    Recover --> Measure[measurement: egress ledger + cost comparison\n+ hash-chained audit]
    Measure --> Output[Output]
    Govern -- "no valid approval" --> Blocked[Blocked by human gate]
```

See also:

- [Distilled notes](local-model-agents.md)
- [Implementation guide](../docs/implementation-guide.md)
- [Threat model](../docs/threat-model.md)
- [Architecture decisions](../docs/adr.md)
