from fastapi.testclient import TestClient
from robotruth_api.app import app

def test_health():
    c = TestClient(app)
    r = c.get("/api/health")
    assert r.status_code == 200 and r.json()["ok"] is True


from robotruth_api import app as appmod

def test_audit_diff_persists_and_returns_receipt(monkeypatch, tmp_path):
    from robotruth_api.store import FileStore
    monkeypatch.setattr(appmod, "STORE", FileStore(tmp_path))
    c = TestClient(appmod.app)
    diff = ("diff --git a/auth/s.ts b/auth/s.ts\n--- a/auth/s.ts\n+++ b/auth/s.ts\n"
            "@@ -1,2 +1,1 @@\n keep\n-app.use(csrfProtection())\n")
    r = c.post("/api/audit/diff", json={"repo": "o/r", "number": 1, "title": "x", "url": "u", "diff": diff})
    assert r.status_code == 200
    body = r.json()
    assert body["receipt"]["grade"] == "D"
    assert body["id"]
    g = c.get(f"/api/receipt/{body['id']}")
    assert g.status_code == 200 and g.json()["grade"] == "D"

def test_diff_too_large_rejected(monkeypatch, tmp_path):
    from robotruth_api.store import FileStore
    monkeypatch.setattr(appmod, "STORE", FileStore(tmp_path))
    monkeypatch.setattr(appmod.config, "DIFF_MAX_BYTES", 10)
    c = TestClient(appmod.app)
    r = c.post("/api/audit/diff", json={"repo": "o/r", "number": 1, "title": "x", "url": "u", "diff": "x" * 50})
    assert r.status_code == 413


def test_audit_diff_respects_keep_claim_kinds(monkeypatch, tmp_path):
    from robotruth_api import app as appmod
    from robotruth_api.store import FileStore
    from fastapi.testclient import TestClient
    monkeypatch.setattr(appmod, "STORE", FileStore(tmp_path))
    c = TestClient(appmod.app)
    diff = "diff --git a/app/x.ts b/app/x.ts\n--- a/app/x.ts\n+++ b/app/x.ts\n@@ -1,1 +1,2 @@\n a\n+b\n"
    base = {"repo": "o/r", "number": 1, "title": "x", "url": "u", "body": "added tests", "diff": diff}
    full = c.post("/api/audit/diff", json=base).json()["receipt"]
    assert any("no test files" in f["label"] for f in full["unhonored"])
    dropped = c.post("/api/audit/diff", json={**base, "keep_claim_kinds": []}).json()["receipt"]
    assert dropped["unhonored"] == []


def test_repo_scorecard_scores_and_lists(monkeypatch):
    from robotruth_api import app as appmod
    from robotruth.types import PRMeta, Receipt
    from fastapi.testclient import TestClient
    import httpx

    # fake the GitHub "list pulls" call.
    # URL-conditional: TestClient also subclasses httpx.Client, so a blanket patch
    # would intercept c.get("/api/repo/o/r") itself.  Delegate non-GitHub URLs
    # back to the real implementation so the ASGI dispatch still works.
    real_get = httpx.Client.get
    def fake_get(self, url, *args, **kwargs):
        if "api.github.com" in str(url):
            req = httpx.Request("GET", url)
            return httpx.Response(200, json=[{"html_url": "https://github.com/o/r/pull/1"},
                                             {"html_url": "https://github.com/o/r/pull/2"}], request=req)
        return real_get(self, url, *args, **kwargs)
    monkeypatch.setattr(httpx.Client, "get", fake_get)

    # fake audit_pr: PR1 honest (A), PR2 sneaky (D)
    def fake_audit(url, token=None):
        n = int(url.rstrip("/").split("/")[-1])
        pr = PRMeta(repo="o/r", number=n, title=f"PR {n}", url=url)
        if n == 1:
            return Receipt(pr=pr, verdict="HONEST", grade="A")
        return Receipt(pr=pr, verdict="SNEAKY", grade="D")
    monkeypatch.setattr(appmod, "audit_pr", fake_audit)

    c = TestClient(appmod.app)
    data = c.get("/api/repo/o/r").json()
    assert data["repo"] == "o/r"
    assert len(data["items"]) == 2
    assert data["score"] == 50  # 1 of 2 graded A/B


def test_audit_diff_maps_value_error_to_400(monkeypatch, tmp_path):
    # Parity with /api/audit: a parse/validation error from the engine must
    # surface as a clean 400, not a 500 with a stack trace.
    from robotruth_api.store import FileStore
    monkeypatch.setattr(appmod, "STORE", FileStore(tmp_path))
    def boom(*a, **k):
        raise ValueError("bad diff")
    monkeypatch.setattr(appmod, "audit_diff", boom)
    c = TestClient(appmod.app)
    r = c.post("/api/audit/diff", json={"repo": "o/r", "number": 1, "title": "x", "url": "u", "diff": "x"})
    assert r.status_code == 400
    assert "bad diff" in r.json()["detail"]


def test_audit_url_success_still_returns_200(monkeypatch, tmp_path):
    # Guard: the httpx->502 catch must not swallow a normal successful audit.
    from robotruth_api.store import FileStore
    from robotruth.types import PRMeta, Receipt
    monkeypatch.setattr(appmod, "STORE", FileStore(tmp_path))
    def ok(url, token=None, keep_claim_kinds=None):
        return Receipt(pr=PRMeta(repo="o/r", number=1, title="x", url=url), verdict="HONEST", grade="A")
    monkeypatch.setattr(appmod, "audit_pr", ok)
    c = TestClient(appmod.app)
    r = c.post("/api/audit", json={"url": "https://github.com/o/r/pull/1"})
    assert r.status_code == 200 and r.json()["receipt"]["grade"] == "A"


def test_audit_url_github_failure_is_502_not_500(monkeypatch, tmp_path):
    import httpx
    from robotruth_api.store import FileStore
    monkeypatch.setattr(appmod, "STORE", FileStore(tmp_path))
    def rate_limited(url, token=None, keep_claim_kinds=None):
        req = httpx.Request("GET", "https://api.github.com/x")
        raise httpx.HTTPStatusError("403", request=req, response=httpx.Response(403, request=req))
    monkeypatch.setattr(appmod, "audit_pr", rate_limited)
    c = TestClient(appmod.app)
    r = c.post("/api/audit", json={"url": "https://github.com/o/r/pull/1"})
    assert r.status_code == 502
    assert "GitHub" in r.json()["detail"]


def test_repo_scorecard_github_failure_is_502_not_500(monkeypatch):
    import httpx
    real_get = httpx.Client.get
    def fake_get(self, url, *args, **kwargs):
        if "api.github.com" in str(url):
            req = httpx.Request("GET", url)
            return httpx.Response(403, request=req, text="rate limited")
        return real_get(self, url, *args, **kwargs)
    monkeypatch.setattr(httpx.Client, "get", fake_get)
    c = TestClient(appmod.app)
    r = c.get("/api/repo/o/r")
    assert r.status_code == 502
    assert "GitHub" in r.json()["detail"]


def test_wall_collects_sneaky_receipts(monkeypatch, tmp_path):
    from robotruth_api import app as appmod
    from robotruth_api.store import FileStore
    from fastapi.testclient import TestClient
    monkeypatch.setattr(appmod, "STORE", FileStore(tmp_path))
    c = TestClient(appmod.app)
    sneaky = ("diff --git a/auth/s.ts b/auth/s.ts\n--- a/auth/s.ts\n+++ b/auth/s.ts\n"
              "@@ -1,2 +1,1 @@\n keep\n-app.use(csrfProtection())\n")
    c.post("/api/audit/diff", json={"repo": "o/r", "number": 1, "title": "x", "url": "u", "diff": sneaky})
    items = c.get("/api/wall").json()["items"]
    assert len(items) == 1
    assert items[0]["verdict"] in ("SNEAKY", "LIAR")
    assert items[0]["author"] is None  # no bot author -> anonymized
