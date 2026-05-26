from __future__ import annotations
import re
from .types import Claim

# Each claim regex matches an active assertion of the claim. We dropped 'with'
# from the test verbs because "compatible with tests" / "issue with tests in CI"
# would fire incorrectly. Verbs now require an authoring stance (add/include/
# write/cover) — passive prose can't trip the parser.
_TEST_RE = re.compile(
    r"\b(add(?:ed|s|ing)?|includ(?:e|ed|es|ing)|wrote|writ(?:e|es|ing)|"
    r"cover(?:ed|s|ing)?|introduce(?:d|s)?)\b[^.\n]*\btests?\b",
    re.I,
)
_NO_DEPS_RE = re.compile(r"\bno\b[^.\n]*\b(dependenc(?:y|ies)|packages?|deps)\b", re.I)
_NO_BREAKING_RE = re.compile(r"\bno\b[^.\n]*\bbreaking\b", re.I)
_SCOPE_ONLY_RE = re.compile(r"\b(only|just|solely|merely)\b", re.I)

# Negation guard: if the same sentence/clause first asserts "did not" or "no"
# adjacent to a claim word, drop the claim. Catches "we did NOT add tests" and
# "no tests added" without breaking on "no breaking changes" (which is the
# intended claim, not a negation of one).
_NEGATED_TEST_RE = re.compile(
    r"\b(?:not?|didn'?t|haven'?t|hasn'?t|won'?t|never)\b[^.\n]*\btests?\b",
    re.I,
)

_CUTOFF_RE = re.compile(
    r"(?is)("
    # Bot/release auto-content
    r"<details>|<!--|\[//\]:|"
    r"#{1,6}\s*release notes|#{1,6}\s*changelog|#{1,6}\s*commits|"
    r"dependabot will resolve|signed-off-by:|"
    # GitHub PR template scaffolding that often contains *future-tense* claims
    # in unchecked checkboxes (e.g. "- [ ] add tests"). These are TODO lists,
    # not assertions of completed work — anything below the marker is dropped.
    r"#{1,6}\s*(?:test\s*plan|checklist|todo|future\s*work|"
    r"how\s*was\s*(?:this\s*)?(?:change\s*)?tested|how\s*to\s*test|"
    r"reviewers?\s*checklist|out\s*of\s*scope)"
    r")"
)
_TAG_RE = re.compile(r"<[^>]+>")
_UNCHECKED_BOX_RE = re.compile(r"^\s*[-*]\s*\[\s*\]\s.*$", re.MULTILINE)


def _human_body(body: str) -> str:
    """Keep only the human-written lead of a PR body: cut at the first
    auto-generated/changelog/template marker, then strip HTML tags and any
    surviving unchecked checkboxes (unchecked = aspirational, not asserted)."""
    if not body:
        return ""
    m = _CUTOFF_RE.search(body)
    lead = body[: m.start()] if m else body
    lead = _UNCHECKED_BOX_RE.sub(" ", lead)
    return _TAG_RE.sub(" ", lead)


def extract_claims(title: str, body: str) -> list[Claim]:
    text = f"{title}\n{_human_body(body)}"
    claims: list[Claim] = []
    if _TEST_RE.search(text) and not _NEGATED_TEST_RE.search(text):
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
