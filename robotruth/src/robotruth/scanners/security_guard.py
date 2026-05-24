from __future__ import annotations
import re
from ..types import Flag
from ..claims import Claim
from ..diffparse import Diff

# High-signal auth/security guard tokens, curated. Bare 'helmet'/'cors' removed
# (collide with react-helmet and the ubiquitous substring 'cors'). 'permission'
# narrowed to call-like forms only.
_GUARD_RE = re.compile(
    r"\b(csrf|csrfProtection|csrfToken|authenticate|authoriz\w*|"
    r"login_required|requires?_auth|requireAuth|verifyToken|checkAuth|"
    r"isAuthenticated|ensureAuth|ensureLoggedIn|permission_required|hasPermission)\b",
    re.I,
)
_COMMENT_RE = re.compile(r"^\s*(#|//|/\*|\*|<!--)")


def _is_guard_usage(line: str) -> bool:
    """True only if the line USES a guard as code: a call `tok(...)` or a
    decorator `@...` — not a bare identifier, an import, or a comment."""
    if _COMMENT_RE.match(line):
        return False
    if not _GUARD_RE.search(line):
        return False
    return ("(" in line) or line.lstrip().startswith("@")


def scan(diff: Diff, claims: list[Claim]) -> list[Flag]:
    out: list[Flag] = []
    for f in diff.files:
        added_blob = "\n".join(a.content for a in f.added)
        for rem in f.removed:
            if not _is_guard_usage(rem.content):
                continue
            m = _GUARD_RE.search(rem.content)
            # Rename guard: same token also added in this file => moved, not removed.
            if m and re.search(re.escape(m.group(0)), added_blob, re.I):
                continue
            out.append(Flag(
                label="Security guard removed/weakened",
                file=f.path,
                severity="critical",
                evidence=f"removed: {rem.content.strip()[:120]}",
            ))
    return out
