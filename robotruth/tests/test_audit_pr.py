import robotruth.engine as engine
from robotruth.types import PRMeta


def test_audit_pr_wires_url_to_receipt(monkeypatch):
    def fake_fetch(owner, repo, number, **kw):
        return PRMeta(repo=f"{owner}/{repo}", number=number, title="Add dark mode",
                      url="u", body="only settings"), \
               "diff --git a/auth/s.ts b/auth/s.ts\n--- a/auth/s.ts\n+++ b/auth/s.ts\n@@ -1,2 +1,1 @@\n keep\n-app.use(csrfProtection())\n"
    monkeypatch.setattr(engine, "fetch_pr", fake_fetch)
    r = engine.audit_pr("https://github.com/o/r/pull/7")
    assert r.pr.number == 7
    assert any("Security guard" in f.label for f in r.undisclosed)
