from robotruth.diffparse import parse_diff
from robotruth.claims import Claim
from robotruth.scanners.scope_drift import scan


def _diff(paths):
    return parse_diff("".join(
        f"diff --git a/{p} b/{p}\n--- a/{p}\n+++ b/{p}\n@@ -1,1 +1,2 @@\n a\n+b\n" for p in paths
    ))


def test_flags_broad_scope_with_only_claim():
    claims = [Claim(kind="scope_only", value="only dark mode")]
    flags = scan(_diff(["ui/a.ts", "auth/b.ts", "infra/c.ts", "api/d.ts"]), claims)
    assert len(flags) == 1 and flags[0].severity == "moderate" and flags[0].file == ""


def test_no_flag_without_scope_claim():
    assert scan(_diff(["ui/a.ts", "auth/b.ts", "infra/c.ts", "api/d.ts"]), []) == []


def test_no_flag_on_code_plus_tests_plus_docs():
    # honest PR: src + tests + docs (3 areas) must NOT flag
    claims = [Claim(kind="scope_only", value="only fix dark mode")]
    assert scan(_diff(["src/a.ts", "tests/a.test.ts", "docs/x.md"]), claims) == []


def test_no_flag_when_scope_is_narrow():
    claims = [Claim(kind="scope_only", value="only x")]
    assert scan(_diff(["ui/a.ts", "ui/b.ts"]), claims) == []
