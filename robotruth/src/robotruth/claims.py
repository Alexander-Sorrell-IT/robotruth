from __future__ import annotations
import re
from .types import Claim

_TEST_RE = re.compile(r"\b(add(?:ed|s)?|includ(?:e|ed|es)|with|wrote)\b[^.\n]*\btests?\b", re.I)
_NO_DEPS_RE = re.compile(r"\bno\b[^.\n]*\b(dependenc(?:y|ies)|packages?|deps)\b", re.I)
_NO_BREAKING_RE = re.compile(r"\bno\b[^.\n]*\bbreaking\b", re.I)
_SCOPE_ONLY_RE = re.compile(r"\b(only|just|solely|merely)\b", re.I)

_CUTOFF_RE = re.compile(
    r"(?is)(<details>|#{1,6}\s*release notes|#{1,6}\s*changelog|"
    r"#{1,6}\s*commits|dependabot will resolve|signed-off-by:|"
    r"<!--|\[//\]:)"
)
_TAG_RE = re.compile(r"<[^>]+>")


def _human_body(body: str) -> str:
    """Keep only the human-written lead of a PR body: cut at the first
    auto-generated/changelog marker, then strip HTML tags."""
    if not body:
        return ""
    m = _CUTOFF_RE.search(body)
    lead = body[: m.start()] if m else body
    return _TAG_RE.sub(" ", lead)


def extract_claims(title: str, body: str) -> list[Claim]:
    text = f"{title}\n{_human_body(body)}"
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
