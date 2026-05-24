from __future__ import annotations
import os
import httpx
from .types import PRMeta

_API = "https://api.github.com"


def fetch_pr(owner: str, repo: str, number: int, *, token: str | None = None,
             client: httpx.Client | None = None) -> tuple[PRMeta, str]:
    token = token or os.environ.get("GITHUB_TOKEN")
    headers = {"Accept": "application/vnd.github+json", "User-Agent": "robotruth"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    owned = client is None
    client = client or httpx.Client(timeout=15)
    url = f"{_API}/repos/{owner}/{repo}/pulls/{number}"
    try:
        meta_r = client.get(url, headers=headers)
        if meta_r.status_code == 404:
            raise LookupError(f"PR not found or private: {owner}/{repo}#{number}")
        meta_r.raise_for_status()
        m = meta_r.json()
        diff_headers = {**headers, "Accept": "application/vnd.github.v3.diff"}
        diff_r = client.get(url, headers=diff_headers)
        diff_r.raise_for_status()
        pr = PRMeta(
            repo=f"{owner}/{repo}", number=number,
            title=m.get("title", ""), url=m.get("html_url", ""),
            body=m.get("body") or "", author=(m.get("user") or {}).get("login"),
        )
        return pr, diff_r.text
    finally:
        if owned:
            client.close()
