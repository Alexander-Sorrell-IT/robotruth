from __future__ import annotations
from mcp.server.fastmcp import FastMCP
from robotruth.engine import audit_pr as _audit_pr
from robotruth.types import Receipt

mcp = FastMCP("robotruth")


def _format(r: Receipt) -> str:
    lines = [
        f"RoboTruth — {r.pr.repo} #{r.pr.number}",
        f'"{r.pr.title}"',
        f"VERDICT: {r.verdict}   GRADE: {r.grade}",
        "",
    ]
    if r.undisclosed:
        lines.append("[!] Did, but didn't mention:")
        lines += [f"  - {f.label}" + (f" ({f.file}:{f.line})" if f.file else "") for f in r.undisclosed]
    if r.unhonored:
        lines.append("[x] Claimed, but not found:")
        lines += [f"  - {f.label}" for f in r.unhonored]
    if r.delivered:
        lines.append("[ok] Claimed & delivered:")
        lines += [f"  - {f.label}" for f in r.delivered]
    lines += ["", f"{r.math} — deterministic, no AI opinions."]
    return "\n".join(lines)


@mcp.tool()
def audit_pr(url: str) -> str:
    """Audit a public GitHub Pull Request for honesty.

    Compares what the PR's title/description CLAIMED against what the diff
    ACTUALLY did, and returns a deterministic "receipt": a verdict
    (HONEST / MOSTLY HONEST / SNEAKY / LIAR), a letter grade, and every
    undisclosed or dangerous change flagged with file:line. Use this to check
    whether an AI-written PR did only what it said it would.

    Args:
        url: A public GitHub pull request URL, e.g. https://github.com/owner/repo/pull/123
    """
    receipt = _audit_pr(url)
    return _format(receipt)


def main() -> None:
    mcp.run()


if __name__ == "__main__":
    main()
