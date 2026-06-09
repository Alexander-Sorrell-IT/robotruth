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


def test_unhonored_when_no_deps_claimed_but_go_mod_changed():
    delivered, unhonored = verify_claims(_diff(["go.mod"]), [Claim(kind="no_deps")])
    assert delivered == [] and len(unhonored) == 1


def test_unhonored_when_no_deps_claimed_but_cargo_changed():
    delivered, unhonored = verify_claims(_diff(["Cargo.toml"]), [Claim(kind="no_deps")])
    assert delivered == [] and len(unhonored) == 1


def test_lockfile_only_churn_is_not_a_broken_no_deps_claim():
    # A "no new dependencies" claim with ONLY a lockfile churning (no manifest change) is
    # NOT a lie — lockfiles re-resolve automatically. Must be honored, not unhonored.
    # (Repro of the pathfinder-ai#390 false positive.)
    for lock in ["package-lock.json", "yarn.lock", "poetry.lock", "go.sum", "Cargo.lock"]:
        delivered, unhonored = verify_claims(_diff([lock]), [Claim(kind="no_deps")])
        assert unhonored == [], f"{lock}-only churn falsely flagged as a broken no_deps claim"
        assert len(delivered) == 1


def test_manifest_change_still_flagged_even_with_lockfile():
    # If a manifest DID change (alongside its lockfile), the no_deps claim is genuinely broken.
    delivered, unhonored = verify_claims(_diff(["package.json", "package-lock.json"]), [Claim(kind="no_deps")])
    assert delivered == [] and len(unhonored) == 1
