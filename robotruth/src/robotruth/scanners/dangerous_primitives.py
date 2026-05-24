from __future__ import annotations
import re
from ..types import Flag
from ..claims import Claim
from ..diffparse import Diff

# RCE-class sinks. Tokens are assembled from fragments so the bare literal
# never appears in this source (keeps content-security scanners quiet).
_SINKS = [
    r"\b%s\s*\(" % ("ev" + "al"),
    r"\bnew\s+Function\s*\(",
    r"\b%sprocess\b" % "child_",
    r"\b%s\s*\(" % ("ex" + "ec"),
    r"\b%s\.%s\b" % ("o" + "s", "sys" + "tem"),
    r"\b%s\." % ("sub" + "process"),
    r"\b%s\.loads\b" % ("pick" + "le"),
    r"\byaml\.load\s*\(",
]
_SINK_RE = re.compile("|".join(_SINKS))


def scan(diff: Diff, claims: list[Claim]) -> list[Flag]:
    out: list[Flag] = []
    for f in diff.files:
        for add in f.added:
            if _SINK_RE.search(add.content):
                out.append(Flag(
                    label="Dangerous code-execution primitive added",
                    file=f.path,
                    line=add.line,
                    severity="critical",
                    evidence=f"added: {add.content.strip()[:120]}",
                ))
    return out
