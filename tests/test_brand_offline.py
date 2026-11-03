"""Brand-check and offline-contract tests."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from local_model_agents import brand

ROOT = Path(__file__).resolve().parents[1]


def test_blocklist_is_non_empty():
    assert len(brand.BLOCKLIST_HASHES) >= 5
    for digest in brand.BLOCKLIST_HASHES:
        assert len(digest) == 64  # SHA-256 hex, no plain names stored


def test_hash_matcher_flags_blocklisted_digest():
    digest = next(iter(brand.BLOCKLIST_HASHES))
    assert brand.matches_hash(digest) is True
    assert brand.matches_hash("0" * 64) is False


def test_fictional_company_name_not_flagged():
    assert brand.scan_text("Vexmere Edge field team weekly notes") == []


def test_no_network_imports_in_package():
    # The suite runs fully offline: package modules must not import
    # network libraries. (Checked statically over the source tree.)
    banned = ("import socket", "import requests", "import urllib", "import httpx")
    for path in (ROOT / "src").rglob("*.py"):
        text = path.read_text()
        for term in banned:
            assert term not in text, f"{term} found in {path}"


def test_simulated_flag_on_every_inference_path():
    from local_model_agents.inference import SimulatedLocalModel

    model = SimulatedLocalModel()
    for task in ("summarize notes", "blorpt zzz unknown"):
        assert model.respond(task).simulated is True
