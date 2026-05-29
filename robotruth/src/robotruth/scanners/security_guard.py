from __future__ import annotations
import re
from ..types import Flag
from ..claims import Claim
from ..diffparse import Diff
from ._paths import is_non_code_path

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
    decorator `@...` — not a bare identifier, an import, string, or comment."""
    if _COMMENT_RE.match(line):
        return False
    m = _GUARD_RE.search(line)
    if not m:
        return False
    if line.lstrip().startswith("@"):
        return True
    # If the token is inside a string literal (odd number of quotes before it),
    # it's log/error text — not a code usage.
    before = line[: m.start()]
    if before.count('"') % 2 == 1 or before.count("'") % 2 == 1:
        return False
    return "(" in line


def _all_added_guard_tokens(diff: Diff) -> set[str]:
    """Every guard token appearing in any added line, across the whole diff.
    A removal whose token shows up here is a refactor (e.g. @login_required
    moved from views/foo.py into middleware/auth.py), not a security regression.
    Brand-fatal otherwise: legitimate hardening passes that re-home auth
    decorators get graded critical."""
    tokens: set[str] = set()
    for f in diff.files:
        # Same non-code filter as the removal loop: a guard token in a doc
        # code-fence or test file must not count as a rename target and mask a
        # genuine removal in production code.
        if is_non_code_path(f.path):
            continue
        for add in f.added:
            if not _is_guard_usage(add.content):
                continue
            for m in _GUARD_RE.finditer(add.content):
                tokens.add(m.group(0).lower())
    return tokens


def scan(diff: Diff, claims: list[Claim]) -> list[Flag]:
    out: list[Flag] = []
    added_tokens = _all_added_guard_tokens(diff)
    for f in diff.files:
        # Removals inside tests/docs/examples are content, not a security
        # regression — a tutorial code-fence or a test refactor that drops a
        # decorator must never raise a brand-fatal critical flag (§13).
        if is_non_code_path(f.path):
            continue
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
                line=rem.line,
                severity="critical",
                evidence=f"removed: {rem.content.strip()[:120]}",
            ))
    return out
