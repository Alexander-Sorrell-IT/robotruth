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
