from __future__ import annotations
from ..types import Flag
from ..claims import Claim
from ..diffparse import Diff

# Conservative: only flag when a narrow-scope claim coincides with changes
# spanning MANY top-level areas (>3), to avoid firing on normal monorepo or
# code+test+docs PRs.
_THRESHOLD = 3


def scan(diff: Diff, claims: list[Claim]) -> list[Flag]:
    if not any(c.kind == "scope_only" for c in claims):
        return []
    topdirs = {(p.split("/", 1)[0] if "/" in p else ".") for p in diff.paths}
    if len(topdirs) <= _THRESHOLD:
        return []
    return [Flag(
        label="Broad scope despite 'only'/'just' claim",
        file="",
        severity="moderate",
        evidence=(f"touched {len(topdirs)} top-level areas: {', '.join(sorted(topdirs))}; "
                  f"files: {', '.join(sorted(diff.paths))[:200]}"),
    )]
