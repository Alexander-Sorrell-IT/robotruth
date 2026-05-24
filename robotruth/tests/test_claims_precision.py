from robotruth.claims import extract_claims

DEPENDABOT_BODY = """Bumps katex from 0.16.44 to 0.16.47.
<details>
<summary>Release notes</summary>
<p>only closes a note when used on a new line</p>
<li>fix: add tests for the new path</li>
</details>
Dependabot will resolve any conflicts with this PR.
"""


def test_ignores_changelog_prose_in_body():
    # 'only' and 'tests' appear ONLY inside the auto-generated changelog -> no claims
    claims = extract_claims("chore(deps): bump katex", DEPENDABOT_BODY)
    assert claims == []


def test_keeps_human_lead_paragraph_claims():
    body = "Added tests for the toggle. Only touches settings.\n<details><summary>x</summary>noise</details>"
    kinds = {c.kind for c in extract_claims("Add dark mode", body)}
    assert "adds_tests" in kinds and "scope_only" in kinds
