from robotruth_api.store import FileStore

def test_put_get_roundtrip(tmp_path):
    s = FileStore(tmp_path)
    rid = s.put({"verdict": "LIAR", "grade": "F"})
    assert isinstance(rid, str) and len(rid) >= 6
    assert s.get(rid)["grade"] == "F"

def test_get_missing_returns_none(tmp_path):
    assert FileStore(tmp_path).get("nope") is None
