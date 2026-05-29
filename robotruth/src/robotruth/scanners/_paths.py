from __future__ import annotations
import re

# Shared by the scanners that *suppress* findings in non-production files
# (dangerous_primitives, security_guard) so an honest test or doc never trips a
# brand-fatal critical flag (§13). One definition on purpose: when each scanner
# had its own notion of "test file" (none / partial / dir-only), honest PRs got
# false "Caught!" verdicts depending on which scanner fired.
#
# Strict by design: a sink or guard-removal hidden in a file merely *named* like
# a test (e.g. test_payload.py) is a deliberate, documented blind spot — traded
# for zero false positives on honest test/doc files (precision > recall).
# Anchored with (^|/) on the basename so substrings ("latest_release.py",
# "contest.py", "attestation.py") are still scanned as real code.
#
# Note: verify.py deliberately uses a *looser* "test"-substring check — its job
# is to *credit* test coverage, where over-matching is harmless. Suppression
# needs this stricter definition; the two are intentionally separate.
_NON_CODE_PATH_RE = re.compile(
    r"(^|/)(tests?|docs?|examples?|fixtures?|samples?|spec|specs|benchmarks?)/"
    r"|\.(md|rst|txt|adoc|asciidoc)$"
    # Test files by filename convention (pytest test_*.py / *_test.py /
    # conftest.py, Go *_test.go, JS/TS *.test.* / *.spec.*) live next to source.
    r"|(^|/)conftest\.py$"
    r"|(^|/)test_[^/]+\.py$"
    r"|(^|/)[^/]+_test\.(py|go)$"
    r"|\.(test|spec)\.[jt]sx?$",
    re.I,
)


def is_non_code_path(path: str) -> bool:
    """True for test/doc/example/fixture paths — content, not production code."""
    return _NON_CODE_PATH_RE.search(path) is not None
