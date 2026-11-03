"""Cost measurement: local pattern vs cloud pattern, same task set.

Parameters are illustrative model parameters for the comparison, not
vendor prices, and are labelled with an as-of date. Local cost is
lower by construction: the local pattern pays an amortised per-task
device cost, while the cloud pattern pays a per-token-style per-task
charge an order of magnitude higher. Negative inputs are rejected.
"""

from __future__ import annotations

from dataclasses import dataclass

AS_OF = "2026-11-03"


@dataclass(frozen=True)
class CostModel:
    local_per_task: float = 0.0002
    cloud_per_task: float = 0.0040
    as_of: str = AS_OF

    def __post_init__(self) -> None:
        if self.local_per_task < 0 or self.cloud_per_task < 0:
            raise ValueError("cost rates must not be negative")

    def compare(self, task_count: int) -> dict:
        if task_count < 0:
            raise ValueError("task_count must not be negative")
        local = round(self.local_per_task * task_count, 6)
        cloud = round(self.cloud_per_task * task_count, 6)
        saving = round(cloud - local, 6)
        return {
            "task_count": task_count,
            "local_total": local,
            "cloud_total": cloud,
            "saving": saving,
            "local_cheaper": local < cloud if task_count > 0 else local <= cloud,
            "as_of": self.as_of,
            "note": "Illustrative model parameters, not vendor prices.",
        }
