"""Build a 30-PR bot-authored corpus by auditing real PRs across major repos.

Output: JSON list of receipts keyed by PR URL. Feeds the Bot Leaderboard and
the 1000-PR "AI Honesty Index" benchmark.

Usage:
    GITHUB_TOKEN=ghp_... python scripts/build_corpus.py --out corpus.json --n 30
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
import urllib.parse
import urllib.request
from typing import Iterable

# Make engine importable when run from repo root.
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from robotruth.engine import audit_pr  # noqa: E402

GITHUB_SEARCH_URL = "https://api.github.com/search/issues"

# Bot author logins that produce real PRs with claim-bearing descriptions.
BOT_LOGINS = [
    "dependabot[bot]",
    "renovate[bot]",
    "github-actions[bot]",
    "pre-commit-ci[bot]",
    "sweep-ai[bot]",
    "aider-ai[bot]",
]


def gh_get(url: str, token: str) -> dict:
    req = urllib.request.Request(
        url,
        headers={
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": "robotruth-corpus-builder",
        },
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read())


def discover_bot_prs(token: str, per_bot: int = 10) -> list[dict]:
    """Search GitHub for merged PRs authored by known bots; return raw items."""
    items: list[dict] = []
    for bot in BOT_LOGINS:
        q = f"is:pr is:merged author:{bot}"
        params = urllib.parse.urlencode(
            {"q": q, "sort": "updated", "order": "desc", "per_page": per_bot}
        )
        url = f"{GITHUB_SEARCH_URL}?{params}"
        try:
            data = gh_get(url, token)
        except Exception as e:
            print(f"[!] search failed for {bot}: {e}", file=sys.stderr)
            continue
        found = data.get("items", []) or []
        print(f"[+] {bot}: {len(found)} PRs")
        items.extend(found)
        time.sleep(2)  # respect GitHub search rate limit (30/min auth)
    return items


def diversify(items: list[dict], n: int) -> list[dict]:
    """Pick a diverse sample: round-robin across (bot, repo) tuples until N."""
    by_bucket: dict[tuple[str, str], list[dict]] = {}
    for it in items:
        author = (it.get("user") or {}).get("login", "unknown")
        repo_url = it.get("repository_url", "")
        repo = repo_url.split("/repos/", 1)[-1] if "/repos/" in repo_url else ""
        by_bucket.setdefault((author, repo), []).append(it)
    buckets = list(by_bucket.values())
    picked: list[dict] = []
    i = 0
    while len(picked) < n and buckets:
        bucket = buckets[i % len(buckets)]
        if bucket:
            picked.append(bucket.pop(0))
        if not bucket:
            buckets.pop(i % len(buckets))
            if not buckets:
                break
            continue
        i += 1
    return picked[:n]


def audit_items(items: Iterable[dict], token: str) -> list[dict]:
    out: list[dict] = []
    for it in items:
        url = it.get("pull_request", {}).get("html_url") or it.get("html_url")
        if not url:
            continue
        print(f"[+] auditing {url}")
        try:
            receipt = audit_pr(url, token=token)
            out.append(json.loads(receipt.model_dump_json()))
        except Exception as e:
            print(f"[!] audit failed for {url}: {e}", file=sys.stderr)
        time.sleep(1)  # be gentle with PR-fetch endpoint
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="corpus.json")
    ap.add_argument("--n", type=int, default=30)
    ap.add_argument("--per-bot", type=int, default=10)
    args = ap.parse_args()

    token = os.environ.get("GITHUB_TOKEN")
    if not token:
        print("error: GITHUB_TOKEN env var required", file=sys.stderr)
        return 2

    items = discover_bot_prs(token, per_bot=args.per_bot)
    if not items:
        print("error: no PRs discovered", file=sys.stderr)
        return 1
    picked = diversify(items, args.n)
    print(f"[+] auditing {len(picked)} PRs")
    receipts = audit_items(picked, token)

    out_path = args.out
    with open(out_path, "w") as f:
        json.dump(receipts, f, indent=2)
    print(f"[+] wrote {len(receipts)} receipts -> {out_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
