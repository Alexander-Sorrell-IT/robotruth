from robotruth.types import PRMeta, Receipt, Flag
from robotruth_mcp.server import _format, mcp


def _receipt():
    return Receipt(
        pr=PRMeta(repo="o/r", number=7, title="add dark mode", url="u"),
        verdict="SNEAKY", grade="D",
        undisclosed=[Flag(label="Security guard removed/weakened", file="auth/s.ts", line=88, severity="critical")],
        unhonored=[Flag(label="Claimed to add tests, but no test files changed", severity="moderate")],
        delivered=[], parsed_claims=["claims to add tests"], math="D: 1 undisclosed (1 critical), 1 unhonored; score=4",
    )


def test_format_includes_verdict_grade_and_flags():
    out = _format(_receipt())
    assert "SNEAKY" in out and "GRADE: D" in out
    assert "auth/s.ts:88" in out
    assert "no test files" in out
    assert "deterministic" in out


def test_server_named_robotruth():
    assert mcp.name == "robotruth"
