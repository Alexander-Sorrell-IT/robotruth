from robotruth.diffparse import parse_diff

SAMPLE = """diff --git a/app/theme.ts b/app/theme.ts
index 111..222 100644
--- a/app/theme.ts
+++ b/app/theme.ts
@@ -1,1 +1,2 @@
 export const x = 1
+export const dark = true
diff --git a/auth/session.ts b/auth/session.ts
index 333..444 100644
--- a/auth/session.ts
+++ b/auth/session.ts
@@ -10,3 +10,2 @@
 const a = 1
-app.use(csrfProtection())
 const b = 2
"""

def test_parses_added_and_removed():
    d = parse_diff(SAMPLE)
    assert set(d.paths) == {"app/theme.ts", "auth/session.ts"}
    theme = next(f for f in d.files if f.path == "app/theme.ts")
    assert theme.added[0].content == "export const dark = true"
    assert theme.added[0].line == 2
    auth = next(f for f in d.files if f.path == "auth/session.ts")
    assert any("csrfProtection" in r.content for r in auth.removed)
