from robotruth.claims import extract_claims, humanize

def test_detects_test_and_scope_claims():
    claims = extract_claims("Add dark mode toggle (only settings)", "Added tests for the toggle.")
    kinds = {c.kind for c in claims}
    assert "adds_tests" in kinds
    assert "scope_only" in kinds

def test_detects_no_deps_claim():
    claims = extract_claims("Refactor", "No dependency changes.")
    assert any(c.kind == "no_deps" for c in claims)

def test_no_false_claims_on_plain_text():
    assert extract_claims("Fix typo in README", "") == []

def test_humanize_returns_strings():
    claims = extract_claims("only", "added tests")
    assert all(isinstance(s, str) for s in humanize(claims))


def test_prose_with_tests_does_not_fire():
    # "compatible with tests" / "issue with tests in CI" — used to trip on
    # the 'with' verb. The verb list now requires an authoring stance.
    assert extract_claims("Fix", "Compatible with tests in CI.") == []
    assert extract_claims("Fix", "Issue with tests on Windows.") == []


def test_negated_test_claim_dropped():
    # "we did NOT add tests" must not fire adds_tests.
    claims = extract_claims("Refactor", "We did not add tests; follow-up will.")
    assert not any(c.kind == "adds_tests" for c in claims)
    claims = extract_claims("Refactor", "No tests added in this PR.")
    assert not any(c.kind == "adds_tests" for c in claims)


def test_unchecked_checkbox_not_a_claim():
    # GitHub PR templates often have unchecked boxes like "- [ ] add tests".
    # These are aspirational, not asserted.
    body = "Fixes #123.\n\n## Checklist\n- [ ] add tests\n- [ ] update docs\n"
    claims = extract_claims("Fix bug", body)
    assert not any(c.kind == "adds_tests" for c in claims)


def test_test_plan_section_cut():
    # "## Test plan" header has historically introduced future-tense lists.
    # Treat as a cut marker — anything below is not a positive assertion.
    body = "Bumps axios.\n\n## Test plan\n- Added tests in CI.\n"
    claims = extract_claims("chore: bump axios", body)
    assert not any(c.kind == "adds_tests" for c in claims)


def test_real_authoring_claim_still_fires():
    # Regression guard: the real "we added tests" assertion must still fire.
    claims = extract_claims("Add feature X", "Includes tests for the new flow.")
    assert any(c.kind == "adds_tests" for c in claims)
    claims = extract_claims("Add feature Y", "Added tests covering the edge case.")
    assert any(c.kind == "adds_tests" for c in claims)
