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


def test_cross_file_rename_not_flagged():
    # Legitimate hardening: @login_required moved from views/foo.py into
    # middleware/auth.py. The decorator is removed from one file and added
    # to another — must NOT flag critical (this is the canonical case
    # adversarial red-team identified as same-file-only rename failure).
    d = parse_diff(
        "diff --git a/views/foo.py b/views/foo.py\n"
        "--- a/views/foo.py\n+++ b/views/foo.py\n"
        "@@ -1,3 +1,2 @@\n"
        " from django.shortcuts import render\n"
        "-@login_required\n"
        " def foo(request):\n"
        "diff --git a/middleware/auth.py b/middleware/auth.py\n"
        "--- a/middleware/auth.py\n+++ b/middleware/auth.py\n"
        "@@ -1,1 +1,3 @@\n"
        " from functools import wraps\n"
        "+@login_required\n"
        "+def wrap(view):\n"
    )
    assert scan(d, []) == []


def test_no_flag_on_removal_in_docs_or_tests():
    # A guard token removed from a doc code-fence or a test refactor is content,
    # not a security regression — must NOT raise a brand-fatal critical flag.
    assert scan(_rm("docs/auth-tutorial.md", "@login_required"), []) == []
    assert scan(_rm("README.rst", "app.use(csrfProtection())"), []) == []
    assert scan(_rm("test_views.py", "@login_required"), []) == []
    assert scan(_rm("tests/test_auth.py", "@requireAuth"), []) == []
    assert scan(_rm("auth.spec.ts", "app.use(csrfProtection())"), []) == []


def test_substring_test_path_still_flagged():
    # Over-suppression guard: a real source file that merely contains "test" as a
    # substring (not the test_/_test convention) must STILL flag a removed guard.
    flags = scan(_rm("latest_release.py", "@login_required"), [])
    assert len(flags) == 1 and flags[0].severity == "critical"


def test_no_flag_on_log_line_mentioning_guard_token():
    # logger.info("login_required check") has '(' on the line but the guard
    # token is inside a string literal — must NOT flag critical.
    assert scan(_rm("views/secure.py", 'logger.info("login_required check passed")'), []) == []
    assert scan(_rm("server.ts", 'console.log("csrf token validation failed")'), []) == []


def test_import_only_addition_does_not_mask_removal():
    # Bypass attempt: remove @login_required from a view, add a bare import of
    # login_required in an unrelated file.  The import is not a guard usage
    # (no call parens, no decorator @), so it must NOT suppress the flag.
    d = parse_diff(
        "diff --git a/views/secure.py b/views/secure.py\n"
        "--- a/views/secure.py\n+++ b/views/secure.py\n"
        "@@ -1,3 +1,2 @@\n"
        " from django.shortcuts import render\n"
        "-@login_required\n"
        " def secure(request):\n"
        "diff --git a/utils/helpers.py b/utils/helpers.py\n"
        "--- a/utils/helpers.py\n+++ b/utils/helpers.py\n"
        "@@ -1,1 +1,2 @@\n"
        " x = 1\n"
        "+from django.contrib.auth.decorators import login_required\n"
    )
    flags = scan(d, [])
    assert len(flags) == 1 and flags[0].severity == "critical"


def test_cross_file_removal_still_flagged():
    # If the same token is NOT added back anywhere in the diff, the removal
    # is still a regression. Regression guard: don't let the cross-file
    # rename detection silence true removals.
    d = parse_diff(
        "diff --git a/views/foo.py b/views/foo.py\n"
        "--- a/views/foo.py\n+++ b/views/foo.py\n"
        "@@ -1,3 +1,2 @@\n"
        " from django.shortcuts import render\n"
        "-@login_required\n"
        " def foo(request):\n"
        "diff --git a/views/bar.py b/views/bar.py\n"
        "--- a/views/bar.py\n+++ b/views/bar.py\n"
        "@@ -1,2 +1,3 @@\n"
        " from django.shortcuts import render\n"
        "+# auth handled upstream\n"
        " def bar(request):\n"
    )
    flags = scan(d, [])
    assert len(flags) == 1 and flags[0].severity == "critical"
