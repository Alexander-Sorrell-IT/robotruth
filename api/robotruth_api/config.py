from __future__ import annotations
import os

DIFF_MAX_BYTES = int(os.environ.get("DIFF_MAX_BYTES", str(1_000_000)))
REDIS_URL = os.environ.get("REDIS_URL")
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")
