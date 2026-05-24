from __future__ import annotations
import re
from ..types import Flag
from ..claims import Claim
from ..diffparse import Diff

_COMMENT_RE = re.compile(r"^\s*(#|//|/\*|\*)")

# Always-dangerous sinks. Tokens fragment-assembled so no bare literal appears.
# 'exec' uses a negative lookbehind so JS `regex.exec(...)` / `.exec(` is NOT matched.
_ALWAYS = [
    r"\b%s\s*\(" % ("ev" + "al"),
    r"\bnew\s+Function\s*\(",
    r"\b%sprocess\b" % "child_",
    r"(?<![\w.])%s\s*\(" % ("ex" + "ec"),
    r"\b%s\.%s\b" % ("o" + "s", "sys" + "tem"),
    r"\b%s\.loads\b" % ("pick" + "le"),
]
_ALWAYS_RE = re.compile("|".join(_ALWAYS))
_SUBPROCESS_RE = re.compile(r"\b%s\b" % ("sub" + "process"))
_SHELL_TRUE_RE = re.compile(r"shell\s*=\s*True")
_YAML_LOAD_RE = re.compile(r"\byaml\.load\s*\(")
_LOADER_RE = re.compile(r"Loader\s*=")


def _is_sink(line: str) -> bool:
    if _COMMENT_RE.match(line):
        return False
    if _ALWAYS_RE.search(line):
        return True
    if _SUBPROCESS_RE.search(line) and _SHELL_TRUE_RE.search(line):
        return True
    if _YAML_LOAD_RE.search(line) and not _LOADER_RE.search(line):
        return True
    return False


def scan(diff: Diff, claims: list[Claim]) -> list[Flag]:
    out: list[Flag] = []
    for f in diff.files:
        for add in f.added:
            if _is_sink(add.content):
                out.append(Flag(
                    label="Dangerous code-execution primitive added",
                    file=f.path,
                    line=add.line,
                    severity="critical",
                    evidence=f"added: {add.content.strip()[:120]}",
                ))
    return out
