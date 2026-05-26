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


def _all_added_guard_tokens(diff: Diff) -> set[str]:
    """Every guard token appearing in any added line, across the whole diff.
    A removal whose token shows up here is a refactor (e.g. @login_required
    moved from views/foo.py into middleware/auth.py), not a security regression.
    Brand-fatal otherwise: legitimate hardening passes that re-home auth
    decorators get graded critical."""
    tokens: set[str] = set()
    for f in diff.files:
        for add in f.added:
            if _COMMENT_RE.match(add.content):
                continue
            for m in _GUARD_RE.finditer(add.content):
                tokens.add(m.group(0).lower())
    return tokens


def scan(diff: Diff, claims: list[Claim]) -> list[Flag]:
    out: list[Flag] = []
    added_tokens = _all_added_guard_tokens(diff)
    for f in diff.files:
        for rem in f.removed:
            if not _is_guard_usage(rem.content):
                continue
            m = _GUARD_RE.search(rem.content)
            # Cross-file rename guard: if the same token is added *anywhere* in
            # the diff, treat the removal as a move/refactor, not a regression.
            if m and m.group(0).lower() in added_tokens:
                continue
            out.append(Flag(
                label="Security guard removed/weakened",
                file=f.path,
                severity="critical",
                evidence=f"removed: {rem.content.strip()[:120]}",
            ))
    return out
