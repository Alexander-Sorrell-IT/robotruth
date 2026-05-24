from robotruth.diffparse import parse_diff
from robotruth.scanners.dependencies import scan

DEP = """diff --git a/package.json b/package.json
--- a/package.json
+++ b/package.json
@@ -1,1 +1,2 @@
 {
+  "chroma-js": "^2.4.2",
"""

def test_flags_package_json_change():
    flags = scan(parse_diff(DEP), [])
    assert len(flags) == 1
    assert flags[0].file == "package.json"
    assert flags[0].severity == "moderate"

def test_ignores_source_change():
    src = "diff --git a/app.ts b/app.ts\n--- a/app.ts\n+++ b/app.ts\n@@ -1,1 +1,2 @@\n a\n+b\n"
    assert scan(parse_diff(src), []) == []
