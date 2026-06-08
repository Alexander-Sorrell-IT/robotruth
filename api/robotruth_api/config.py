from __future__ import annotations
import os

DIFF_MAX_BYTES = int(os.environ.get("DIFF_MAX_BYTES", str(1_000_000)))
# Accept whatever a Vercel KV / Upstash Redis integration names the connection
# string, so adding a store in the dashboard "just works" (no rename needed).
REDIS_URL = (
    os.environ.get("REDIS_URL")
    or os.environ.get("KV_URL")
    or os.environ.get("UPSTASH_REDIS_URL")
    or os.environ.get("STORAGE_REDIS_URL")
)
# Upstash REST creds — the serverless-friendly path (HTTP, no persistent TCP
# connection). Preferred over REDIS_URL when present; what the Vercel/Upstash
# integration injects by default.
UPSTASH_REST_URL = os.environ.get("UPSTASH_REDIS_REST_URL") or os.environ.get("KV_REST_API_URL")
UPSTASH_REST_TOKEN = os.environ.get("UPSTASH_REDIS_REST_TOKEN") or os.environ.get("KV_REST_API_TOKEN")
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")
