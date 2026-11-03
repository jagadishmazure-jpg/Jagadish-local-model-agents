"""Hash-chained audit log.

Every entry carries the SHA-256 hash of the previous entry, so any
later edit to an entry breaks verification of every entry after it.
The chain is verified by recomputing each link, not by trusting a
stored "valid" flag.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field


def _digest(index: int, prev_hash: str, event: str, actor: str, details: dict) -> str:
    payload = json.dumps(
        {"index": index, "prev": prev_hash, "event": event,
         "actor": actor, "details": details},
        sort_keys=True,
    )
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


@dataclass
class AuditEntry:
    index: int
    prev_hash: str
    event: str
    actor: str
    details: dict
    digest: str


@dataclass
class AuditLog:
    entries: list = field(default_factory=list)

    def append(self, event: str, actor: str, details: dict | None = None) -> AuditEntry:
        prev = self.entries[-1].digest if self.entries else "GENESIS"
        entry = AuditEntry(
            index=len(self.entries),
            prev_hash=prev,
            event=event,
            actor=actor,
            details=details or {},
            digest=_digest(len(self.entries), prev, event, actor, details or {}),
        )
        self.entries.append(entry)
        return entry

    def verify(self) -> bool:
        prev = "GENESIS"
        for i, entry in enumerate(self.entries):
            if entry.index != i or entry.prev_hash != prev:
                return False
            expected = _digest(i, prev, entry.event, entry.actor, entry.details)
            if entry.digest != expected:
                return False
            prev = entry.digest
        return True
