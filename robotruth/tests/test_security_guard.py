from robotruth.diffparse import parse_diff
from robotruth.scanners.security_guard import scan


def _rm(path, line):
    return parse_diff(f"diff --git a/{path} b/{path}\n--- a/{path}\n+++ b/{path}\n@@ -1,2 +1,1 @@\n keep\n-{line}\n")


def test_flags_removed_csrf_call():
    flags = scan(_rm("auth/session.ts", "app.use(csrfProtection())"), [])
    assert len(flags) == 1 and flags[0].severity == "critical" and flags[0].file == "auth/session.ts"


def test_no_flag_when_nothing_removed():
    diff = parse_diff("diff --git a/x.ts b/x.ts\n--- a/x.ts\n+++ b/x.ts\n@@ -1,1 +1,2 @@\n a\n+b\n")
    assert scan(diff, []) == []


def test_no_flag_on_react_helmet_removal():
    # honest UI refactor removing react-helmet must NOT flag
    assert scan(_rm("pages/Home.tsx", 'import Helmet from "react-helmet"'), []) == []


def test_no_flag_on_removed_comment_mentioning_cors():
    assert scan(_rm("server.ts", "// cors handled at the load balancer"), []) == []


def test_no_flag_on_bare_permission_identifier():
    assert scan(_rm("ui/Table.tsx", "const permissionLevel = 3"), []) == []


def test_rename_not_flagged():
    # csrfProtection removed AND re-added (moved) in same file -> not a removal
    d = parse_diff(
        "diff --git a/a.ts b/a.ts\n--- a/a.ts\n+++ b/a.ts\n"
        "@@ -1,2 +1,2 @@\n keep\n-app.use(csrfProtection())\n+  app.use(csrfProtection())\n"
    )
    assert scan(d, []) == []
