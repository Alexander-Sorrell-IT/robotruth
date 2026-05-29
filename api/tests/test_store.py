from robotruth_api.store import FileStore

def test_put_get_roundtrip(tmp_path):
    s = FileStore(tmp_path)
    rid = s.put({"verdict": "LIAR", "grade": "F"})
    assert isinstance(rid, str) and len(rid) >= 6
    assert s.get(rid)["grade"] == "F"

def test_get_missing_returns_none(tmp_path):
    assert FileStore(tmp_path).get("nope") is None

def test_get_rejects_path_traversal(tmp_path):
    # Defense-in-depth: a crafted id must not escape the store root, even
    # though the HTTP route already blocks slashes at the path converter.
    s = FileStore(tmp_path / "store")
    (tmp_path / "secret.json").write_text('{"leaked": true}')
    assert s.get("../secret") is None
    assert s.get("../../etc/passwd") is None
