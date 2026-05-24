from robotruth.types import Flag, Claim, PRMeta, Receipt

def test_receipt_roundtrips():
    pr = PRMeta(repo="o/r", number=1, title="t", url="u")
    r = Receipt(pr=pr, verdict="HONEST", grade="A")
    assert r.grade == "A"
    assert r.model_dump()["pr"]["repo"] == "o/r"

def test_flag_defaults_line_optional():
    f = Flag(label="x", file="a.py", severity="critical", evidence="e")
    assert f.line is None
