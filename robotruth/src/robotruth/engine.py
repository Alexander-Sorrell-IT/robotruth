from __future__ import annotations
from .types import Receipt, PRMeta
from .diffparse import parse_diff
from .claims import extract_claims, humanize
from .scanners import run_scanners
from .verify import verify_claims
from .grade import grade_and_verdict
from .github import fetch_pr  # noqa: F401  (re-exported for monkeypatching)
from .urls import parse_pr_url


def audit_diff(pr: PRMeta, diff_text: str, *, keep_claim_kinds: list[str] | None = None) -> Receipt:
    diff = parse_diff(diff_text)
    claims = extract_claims(pr.title, pr.body)
    if keep_claim_kinds is not None:
        keep = set(keep_claim_kinds)
        claims = [c for c in claims if c.kind in keep]
    undisclosed = run_scanners(diff, claims)
    delivered, unhonored = verify_claims(diff, claims)
    grade, verdict, math = grade_and_verdict(undisclosed, unhonored)
    return Receipt(
        pr=pr, verdict=verdict, grade=grade,
        delivered=delivered, undisclosed=undisclosed, unhonored=unhonored,
        parsed_claims=humanize(claims), claim_kinds=[c.kind for c in claims], math=math,
    )


def audit_pr(url: str, *, token: str | None = None, keep_claim_kinds: list[str] | None = None) -> Receipt:
    owner, repo, number = parse_pr_url(url)
    pr, diff_text = fetch_pr(owner, repo, number, token=token)
    return audit_diff(pr, diff_text, keep_claim_kinds=keep_claim_kinds)
