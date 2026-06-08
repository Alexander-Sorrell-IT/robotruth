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


def _all_present_guard_tokens(diff: Diff) -> set[str]:
    """Every guard token still present (as a code usage) in the post-image of
    the diff — added lines AND retained context lines — across the whole diff.
    A removal whose token shows up here is a move/refactor, not a regression:
      - added elsewhere: @login_required re-homed from views/foo.py into
        middleware/auth.py;
      - retained as context: an extract-to-helper refactor consolidates the
        repeated `authenticate(...)` call into one shared function, so the call
        survives on an unchanged line while its old per-handler copies are
        removed (the goauth#389 case — graded a brand-fatal critical LIAR
        before this).
    Brand-fatal otherwise: legitimate hardening/refactors get graded critical."""
    tokens: set[str] = set()
    for f in diff.files:
        # Same non-code filter as the removal loop: a guard token in a doc
        # code-fence or test file must not count as a rename target and mask a
        # genuine removal in production code.
        if is_non_code_path(f.path):
            continue
        for content in (a.content for a in f.added):
            if not _is_guard_usage(content):
                continue
            for m in _GUARD_RE.finditer(content):
                tokens.add(m.group(0).lower())
        for content in f.context:
            if not _is_guard_usage(content):
                continue
            for m in _GUARD_RE.finditer(content):
                tokens.add(m.group(0).lower())
    return tokens


def scan(diff: Diff, claims: list[Claim]) -> list[Flag]:
    out: list[Flag] = []
    present_tokens = _all_present_guard_tokens(diff)
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
            # Move/refactor guard: if the same token still exists as a usage
            # anywhere in the post-image (added OR retained context), treat the
            # removal as a move/consolidation, not a regression.
            if m and m.group(0).lower() in present_tokens:
                continue
            out.append(Flag(
                label="Security guard removed/weakened",
                file=f.path,
                line=rem.line,
                severity="critical",
                evidence=f"removed: {rem.content.strip()[:120]}",
            ))
    return out
