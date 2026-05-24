from robotruth.types import PRMeta
from robotruth.engine import audit_diff

_DIFF = "diff --git a/app/x.ts b/app/x.ts\n--- a/app/x.ts\n+++ b/app/x.ts\n@@ -1,1 +1,2 @@\n a\n+b\n"


def test_full_audit_flags_missing_tests_and_exposes_kinds():
    pr = PRMeta(repo="o/r", number=1, title="add feature", url="u", body="added tests")
    r = audit_diff(pr, _DIFF)
    assert "adds_tests" in r.claim_kinds
    assert any("no test files" in f.label for f in r.unhonored)


def test_dropping_claim_removes_its_finding():
    pr = PRMeta(repo="o/r", number=1, title="add feature", url="u", body="added tests")
    r = audit_diff(pr, _DIFF, keep_claim_kinds=[])
    assert r.unhonored == []
    assert r.claim_kinds == []
