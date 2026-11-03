"""Cost-model tests: same task set, local cheaper by construction."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from local_model_agents.cost import CostModel


def test_local_cheaper_than_cloud_on_same_task_set():
    result = CostModel().compare(100)
    assert result["local_total"] == 0.02
    assert result["cloud_total"] == 0.4
    assert result["local_cheaper"] is True
    assert result["saving"] == 0.38


def test_demo_task_set_costs():
    result = CostModel().compare(6)
    assert result["local_total"] == 0.0012
    assert result["cloud_total"] == 0.024
    assert result["local_cheaper"] is True


def test_zero_tasks_zero_cost():
    result = CostModel().compare(0)
    assert result["local_total"] == 0
    assert result["cloud_total"] == 0


def test_negative_task_count_rejected():
    try:
        CostModel().compare(-1)
    except ValueError:
        return
    raise AssertionError("negative task count should raise")


def test_negative_rate_rejected():
    try:
        CostModel(local_per_task=-0.1)
    except ValueError:
        return
    raise AssertionError("negative rate should raise")


def test_as_of_date_present():
    assert CostModel().compare(1)["as_of"] == "2026-11-03"
