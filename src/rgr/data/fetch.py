"""Dataset fetching: pinned upstream files, stdlib urllib, local cache.

No `datasets` dependency for Phase 0 — the raw MBPP/HumanEval files are small,
stable, and pinning exact URLs + SHA256 beats a resolver for reproducibility.
Cache lives in data/cache/ (gitignored). A checksum mismatch is a hard error:
silently changed eval data invalidates every frozen number on the dashboard.
"""

from __future__ import annotations

import hashlib
import urllib.request
from pathlib import Path

CACHE_DIR = Path(__file__).parents[3] / "data" / "cache"


def fetch(url: str, filename: str, sha256: str | None = None) -> Path:
    """Download to cache (once) and return the local path."""
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    path = CACHE_DIR / filename
    if not path.exists():
        with urllib.request.urlopen(url, timeout=60) as response:
            data = response.read()
        path.write_bytes(data)
    if sha256 is not None:
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        if digest != sha256:
            raise RuntimeError(
                f"checksum mismatch for {filename}: expected {sha256}, got {digest} — "
                "eval data changed upstream; do NOT proceed, re-pin deliberately"
            )
    return path
