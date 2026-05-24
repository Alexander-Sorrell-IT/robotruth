from __future__ import annotations
import re
from .types import Claim

_TEST_RE = re.compile(r"\b(add(?:ed|s)?|includ(?:e|ed|es)|with|wrote)\b[^.\n]*\btests?\b", re.I)
_NO_DEPS_RE = re.compile(r"\bno\b[^.\n]*\b(dependenc(?:y|ies)|packages?|deps)\b", re.I)
_NO_BREAKING_RE = re.compile(r"\bno\b[^.\n]*\bbreaking\b", re.I)
_SCOPE_ONLY_RE = re.compile(r"\b(only|just|solely|merely)\b", re.I)


def extract_claims(title: str, body: str) -> list[Claim]:
    text = f"{title}\n{body or ''}"
    claims: list[Claim] = []
    if _TEST_RE.search(text):
        claims.append(Claim(kind="adds_tests", raw="claims to add tests"))
    if _NO_DEPS_RE.search(text):
        claims.append(Claim(kind="no_deps", raw="claims no dependency changes"))
    if _NO_BREAKING_RE.search(text):
        claims.append(Claim(kind="no_breaking", raw="claims no breaking changes"))
    if _SCOPE_ONLY_RE.search(text):
        claims.append(Claim(kind="scope_only", value=title, raw="claims a narrow scope ('only'/'just')"))
    return claims


def humanize(claims: list[Claim]) -> list[str]:
    return [c.raw for c in claims]
