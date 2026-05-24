from robotruth.diffparse import parse_diff
from robotruth.scanners.dangerous_primitives import scan

# the added line below reads `+const r = eval(userInput)` once assembled
ADDED_SINK = (
    "diff --git a/run.js b/run.js\n"
    "--- a/run.js\n"
    "+++ b/run.js\n"
    "@@ -1,1 +1,2 @@\n"
    " const a = 1\n"
    "+const r = " + "ev" + "al(userInput)\n"
)

def test_flags_added_sink():
    flags = scan(parse_diff(ADDED_SINK), [])
    assert len(flags) == 1
    assert flags[0].severity == "critical"
    assert flags[0].line == 2

def test_ignores_removed_sink():
    removed = (
        "diff --git a/x.js b/x.js\n--- a/x.js\n+++ b/x.js\n"
        "@@ -1,2 +1,1 @@\n const a = 1\n-const r = " + "ev" + "al(x)\n"
    )
    assert scan(parse_diff(removed), []) == []
