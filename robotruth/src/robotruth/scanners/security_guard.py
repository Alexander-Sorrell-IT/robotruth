from __future__ import annotations
import re
from ..types import Flag
from ..claims import Claim
from ..diffparse import Diff

_GUARD_RE = re.compile(
    r"\b(csrf|csrfProtection|authenticate|authoriz\w*|permission\w*|login_required|"
    r"requireAuth|verifyToken|checkAuth|isAuthenticated|ensureAuth|helmet|cors)\b",
    re.I,
)


def scan(diff: Diff, claims: list[Claim]) -> list[Flag]:
    out: list[Flag] = []
    for f in diff.files:
        for rem in f.removed:
            if _GUARD_RE.search(rem.content):
                out.append(Flag(
                    label="Security guard removed/weakened",
                    file=f.path,
                    severity="critical",
                    evidence=f"removed: {rem.content.strip()[:120]}",
                ))
    return out
