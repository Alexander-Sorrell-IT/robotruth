from __future__ import annotations
import re

_PR_RE = re.compile(r"github\.com/([^/\s]+)/([^/\s]+)/pull/(\d+)")


def parse_pr_url(url: str) -> tuple[str, str, int]:
    """Return (owner, repo, number) from a GitHub PR URL. Raise ValueError otherwise."""
    m = _PR_RE.search(url.strip())
    if not m:
        raise ValueError(f"Not a GitHub PR URL: {url!r}")
    return m.group(1), m.group(2), int(m.group(3))
