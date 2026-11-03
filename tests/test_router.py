"""Router tests: local-first, sensitive stays local, live-data labelled."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from local_model_agents.router import RouterAgent

R = RouterAgent()


def test_default_route_is_local():
    assert R.route("summarize the weekly notes").destination == "local"


def test_sensitive_task_stays_local():
    route = R.route("tell me the live price of steel", sensitive=True)
    assert route.destination == "local"


def test_redacted_content_stays_local():
    route = R.route("contact [REDACTED-EMAIL] about the live price of steel")
    assert route.destination == "local"


def test_live_data_task_gets_comparison_label():
    route = R.route("tell me the live price of steel")
    assert route.destination == "cloud-pattern-comparison"
    assert "live" in route.reason.lower()


def test_route_reason_always_present():
    for task in ("summarize notes", "tell me the live price of steel"):
        assert R.route(task).reason.strip() != ""
