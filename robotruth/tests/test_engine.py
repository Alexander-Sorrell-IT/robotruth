from robotruth.types import PRMeta
from robotruth.engine import audit_diff

DARKMODE_PR = """diff --git a/settings/Theme.tsx b/settings/Theme.tsx
--- a/settings/Theme.tsx
+++ b/settings/Theme.tsx
@@ -1,1 +1,2 @@
 export const Settings = () => null
+export const Theme = () => null
diff --git a/auth/session.ts b/auth/session.ts
--- a/auth/session.ts
+++ b/auth/session.ts
@@ -10,3 +10,2 @@
 const a = 1
-app.use(csrfProtection())
 const b = 2
diff --git a/package.json b/package.json
--- a/package.json
+++ b/package.json
@@ -1,1 +1,2 @@
 {
+  "chroma-js": "^2.4.2"
"""


def test_darkmode_pr_catches_csrf_and_deps_and_missing_tests():
    pr = PRMeta(repo="o/r", number=482, title="Add dark mode toggle",
                url="https://github.com/o/r/pull/482", body="Added tests for the toggle.")
    r = audit_diff(pr, DARKMODE_PR)
    labels = {f.label for f in r.undisclosed}
    assert any("Security guard" in l for l in labels)
    assert any("Dependency" in l for l in labels)
    assert any("no test files" in f.label for f in r.unhonored)
    assert r.grade in ("D", "F")
    assert r.verdict in ("SNEAKY", "LIAR")
    assert r.parsed_claims
