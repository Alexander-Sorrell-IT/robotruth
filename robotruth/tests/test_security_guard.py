from robotruth.diffparse import parse_diff
from robotruth.scanners.security_guard import scan

REMOVED_CSRF = """diff --git a/auth/session.ts b/auth/session.ts
--- a/auth/session.ts
+++ b/auth/session.ts
@@ -10,3 +10,2 @@
 const a = 1
-app.use(csrfProtection())
 const b = 2
"""

def test_flags_removed_csrf_guard():
    flags = scan(parse_diff(REMOVED_CSRF), [])
    assert len(flags) == 1
    assert flags[0].severity == "critical"
    assert flags[0].file == "auth/session.ts"

def test_no_flag_when_nothing_removed():
    diff = parse_diff("diff --git a/x.ts b/x.ts\n--- a/x.ts\n+++ b/x.ts\n@@ -1,1 +1,2 @@\n a\n+b\n")
    assert scan(diff, []) == []
