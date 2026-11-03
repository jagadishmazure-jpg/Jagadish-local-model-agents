"""Brand/name check.

The blocklist is stored ONLY as SHA-256 hashes -- never as plain
names -- so the check itself cannot leak the names it guards against.
Scanning hashes each token and each adjacent token pair of the input
and compares against the blocklist. The test suite asserts the
blocklist is non-empty and that the fictional company name used in
this repo is not flagged.
"""

from __future__ import annotations

import hashlib
import re

# SHA-256 hex digests of real enterprise names that must never appear
# as clients, partners, or endorsers in this repo's materials. Plain
# names are intentionally not stored here.
BLOCKLIST_HASHES = frozenset({
    "9fbf261b62c1d7c00db73afb81dd97fdf20b3442e36e338cb9359b856a03bdc8",
    "bbdefa2950f49882f295b1285d4fa9dec45fc4144bfb07ee6acc68762d12c2e3",
    "cbc62794911ff31b2864ecd3dbbbee7ebcb7ea41c5a42e2cba377f3cfdb42811",
    "4d748ebd71af03a7c325a5ecef86e3768b71597ba3c08dc26624bfdbd84a0a34",
    "3e808ece8227f5d4fda47690aed90895fc56881b6335d39ace7e8078b240164c",
    "916a98f0fa2a39af1a736b1a3744cb655dc8638a6953e2fb13e39934ab60d55a",
    "7d3194f79e645c42e4396dda38be04766810ec6a00d00aced3ffc2a0a1f1a9ef",
    "c70eca6b0f88f44d81a41311647e50fda1ac454ec04ffd442b0eb4743a993131",
    "9d8ac7e23cd1e212c2af0277e0ba0f4dec4d7c801f78ca59b7a3d89bab16e262",
    "7105a46cb4c2810f0c916e0bb4b4e4ef834ad42040c471b42c96d356a9fd1b21",
})

_TOKEN_RE = re.compile(r"[a-z0-9]+")


def _hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def matches_hash(digest: str) -> bool:
    """Hash-level matcher: True when a digest is on the blocklist."""
    return digest in BLOCKLIST_HASHES


def scan_text(text: str) -> list:
    """Return the blocklisted digests found in ``text`` (usually [])."""
    tokens = _TOKEN_RE.findall(text.lower())
    candidates = list(tokens)
    candidates += [" ".join(pair) for pair in zip(tokens, tokens[1:])]
    return sorted({_hash(c) for c in candidates if _hash(c) in BLOCKLIST_HASHES})
