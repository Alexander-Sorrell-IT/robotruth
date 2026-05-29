from __future__ import annotations
from ..types import Flag
from ..claims import Claim
from ..diffparse import Diff
from ._paths import is_non_code_path

# Conservative: only flag when a narrow-scope claim coincides with changes
# spanning MANY top-level code areas (>3). Tests, docs, examples, and other
# non-code paths are excluded from the count — a standard "code + tests + docs"
# PR should never trigger this regardless of how many directories it touches.
_THRESHOLD = 3


def scan(diff: Diff, claims: list[Claim]) -> list[Flag]:
    if not any(c.kind == "scope_only" for c in claims):
        return []
    code_paths = [p for p in diff.paths if not is_non_code_path(p)]
    topdirs = {(p.split("/", 1)[0] if "/" in p else ".") for p in code_paths}
    if len(topdirs) <= _THRESHOLD:
        return []
    return [Flag(
        label="Broad scope despite 'only'/'just' claim",
        file="",
        severity="moderate",
        evidence=(f"touched {len(topdirs)} top-level code areas: {', '.join(sorted(topdirs))}; "
                  f"files: {', '.join(sorted(code_paths))[:200]}"),
    )]
