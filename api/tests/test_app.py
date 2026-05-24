from fastapi.testclient import TestClient
from robotruth_api.app import app

def test_health():
    c = TestClient(app)
    r = c.get("/api/health")
    assert r.status_code == 200 and r.json()["ok"] is True
