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
