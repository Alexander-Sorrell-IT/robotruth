from robotruth.diffparse import parse_diff
from robotruth.claims import Claim
from robotruth.verify import verify_claims


def _diff(paths):
    return parse_diff("".join(
        f"diff --git a/{p} b/{p}\n--- a/{p}\n+++ b/{p}\n@@ -1,1 +1,2 @@\n a\n+b\n" for p in paths
    ))


def test_unhonored_when_tests_claimed_but_absent():
    delivered, unhonored = verify_claims(_diff(["app/x.ts"]), [Claim(kind="adds_tests")])
    assert delivered == [] and len(unhonored) == 1


def test_delivered_when_tests_present():
    delivered, unhonored = verify_claims(_diff(["app/x.test.ts"]), [Claim(kind="adds_tests")])
    assert len(delivered) == 1 and unhonored == []


def test_unhonored_when_no_deps_claimed_but_deps_changed():
    delivered, unhonored = verify_claims(_diff(["package.json"]), [Claim(kind="no_deps")])
    assert len(unhonored) == 1
