from __future__ import annotations
from ..types import Flag
from ..claims import Claim
from ..diffparse import Diff


def scan(diff: Diff, claims: list[Claim]) -> list[Flag]:
    if not any(c.kind == "scope_only" for c in claims):
        return []
    topdirs = {(p.split("/", 1)[0] if "/" in p else ".") for p in diff.paths}
    if len(topdirs) <= 2:
        return []
    return [Flag(
        label="Broad scope despite 'only'/'just' claim",
        file=", ".join(sorted(diff.paths))[:160],
        severity="moderate",
        evidence=f"touched {len(topdirs)} top-level areas: {', '.join(sorted(topdirs))}",
    )]
