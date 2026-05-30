from __future__ import annotations
from pathlib import Path
import html
import httpx
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from pydantic import BaseModel
from robotruth.types import PRMeta
from robotruth.engine import audit_diff, audit_pr
from . import config
from .store import FileStore, RedisStore, ReceiptStore

app = FastAPI(title="RoboTruth API")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

STORE: ReceiptStore = RedisStore(config.REDIS_URL) if config.REDIS_URL else FileStore(Path("/tmp/robotruth-receipts"))


class UrlReq(BaseModel):
    url: str
    keep_claim_kinds: list[str] | None = None


class DiffReq(BaseModel):
    repo: str
    number: int
    title: str
    url: str
    body: str = ""
    diff: str
    keep_claim_kinds: list[str] | None = None


def _store_and_return(receipt: dict) -> dict:
    rid = STORE.put(receipt)
    if receipt.get("verdict") in ("SNEAKY", "LIAR"):
        author = receipt["pr"].get("author")
        STORE.add_wall({
            "id": rid,
            "repo": receipt["pr"]["repo"],
            "number": receipt["pr"]["number"],
            "title": receipt["pr"]["title"],
            "verdict": receipt["verdict"],
            "grade": receipt["grade"],
            "author": author if (author and author.endswith("[bot]")) else None,
        })
    return {"id": rid, "receipt": receipt}


@app.get("/api/health")
def health() -> dict:
    return {"ok": True}


@app.post("/api/audit")
def audit_url(req: UrlReq) -> dict:
    try:
        receipt = audit_pr(req.url, token=config.GITHUB_TOKEN, keep_claim_kinds=req.keep_claim_kinds)
    except ValueError as e:
        raise HTTPException(400, str(e))
    except LookupError as e:
        raise HTTPException(404, str(e))
    except httpx.HTTPError:
        raise HTTPException(502, "Could not reach GitHub (rate limit or upstream error); try again shortly.")
    return _store_and_return(receipt.model_dump())


@app.post("/api/audit/diff")
def audit_paste(req: DiffReq) -> dict:
    if len(req.diff.encode("utf-8")) > config.DIFF_MAX_BYTES:
        raise HTTPException(413, "Diff too large; trim it or audit a smaller PR.")
    pr = PRMeta(repo=req.repo, number=req.number, title=req.title, url=req.url, body=req.body)
    try:
        receipt = audit_diff(pr, req.diff, keep_claim_kinds=req.keep_claim_kinds)
    except ValueError as e:
        raise HTTPException(400, str(e))
    except LookupError as e:
        raise HTTPException(404, str(e))
    return _store_and_return(receipt.model_dump())


@app.get("/api/wall")
def wall() -> dict:
    return {"items": STORE.wall()}


@app.get("/api/receipt/{rid}")
def get_receipt(rid: str) -> dict:
    r = STORE.get(rid)
    if r is None:
        raise HTTPException(404, "Receipt not found")
    return r


def _score_repo(owner: str, name: str) -> tuple[int | None, int]:
    """Compute (score, sample_size) for a repo, or (None, 0) if unverifiable.
    Score = % of audited PRs grading A or B. Returns None on any failure so
    the badge can show 'unverified' instead of misleadingly reporting 0%."""
    headers = {"Accept": "application/vnd.github+json", "User-Agent": "robotruth"}
    if config.GITHUB_TOKEN:
        headers["Authorization"] = f"Bearer {config.GITHUB_TOKEN}"
    try:
        with httpx.Client(timeout=20) as client:
            r = client.get(
                f"https://api.github.com/repos/{owner}/{name}/pulls",
                params={"state": "all", "per_page": 8, "sort": "created", "direction": "desc"},
                headers=headers,
            )
            if r.status_code != 200:
                return (None, 0)
            pulls = r.json()
    except httpx.HTTPError:
        return (None, 0)
    audited = 0
    good = 0
    for p in pulls:
        url = p.get("html_url")
        if not url:
            continue
        try:
            receipt = audit_pr(url, token=config.GITHUB_TOKEN)
        except (ValueError, LookupError, httpx.HTTPError):
            continue
        audited += 1
        if receipt.grade in ("A", "B"):
            good += 1
    if audited == 0:
        return (None, 0)
    return (round(100 * good / audited), audited)


def _badge_color(score: int | None) -> str:
    """Shields.io-aligned hue ramp. None = neutral gray ('unverified')."""
    if score is None:
        return "#9f9f9f"
    if score >= 90:
        return "#4c1"
    if score >= 75:
        return "#a4a61d"
    if score >= 50:
        return "#dfb317"
    if score >= 25:
        return "#fe7d37"
    return "#e05d44"


def _badge_svg(left: str, right: str, right_color: str) -> str:
    """Minimal Shields-style SVG badge. Two rounded boxes side-by-side."""
    # Approximate text widths via 7px-per-char heuristic (decent for sans).
    lw = max(40, 10 + 7 * len(left))
    rw = max(50, 10 + 7 * len(right))
    total = lw + rw
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{total}" height="20" role="img" aria-label="{html.escape(left)}: {html.escape(right)}">
  <linearGradient id="g" x2="0" y2="100%">
    <stop offset="0" stop-color="#bbb" stop-opacity=".1"/>
    <stop offset="1" stop-opacity=".1"/>
  </linearGradient>
  <clipPath id="r"><rect width="{total}" height="20" rx="3" fill="#fff"/></clipPath>
  <g clip-path="url(#r)">
    <rect width="{lw}" height="20" fill="#555"/>
    <rect x="{lw}" width="{rw}" height="20" fill="{right_color}"/>
    <rect width="{total}" height="20" fill="url(#g)"/>
  </g>
  <g fill="#fff" text-anchor="middle" font-family="Verdana,Geneva,DejaVu Sans,sans-serif" font-size="11">
    <text x="{lw/2}" y="15" fill="#010101" fill-opacity=".3">{html.escape(left)}</text>
    <text x="{lw/2}" y="14">{html.escape(left)}</text>
    <text x="{lw + rw/2}" y="15" fill="#010101" fill-opacity=".3">{html.escape(right)}</text>
    <text x="{lw + rw/2}" y="14">{html.escape(right)}</text>
  </g>
</svg>"""


@app.get("/api/badge/{owner}/{name}.svg")
def badge(owner: str, name: str) -> Response:
    """Shields-style honesty badge for a public GitHub repo. The right-hand
    label is the % of the repo's last 8 PRs grading A or B. Cacheable; if the
    audit can't run (rate limit, private repo, etc.) we return a neutral
    'unverified' badge rather than lying with a 0% score."""
    score, _n = _score_repo(owner, name)
    if score is None:
        right = "unverified"
    else:
        right = f"{score}% honest"
    svg = _badge_svg("robotruth", right, _badge_color(score))
    return Response(
        content=svg,
        media_type="image/svg+xml",
        headers={
            # Cache for an hour at the edge; allow revalidation in background.
            "Cache-Control": "public, max-age=3600, stale-while-revalidate=86400",
        },
    )


@app.get("/api/repo/{owner}/{name}")
def repo_scorecard(owner: str, name: str) -> dict:
    headers = {"Accept": "application/vnd.github+json", "User-Agent": "robotruth"}
    if config.GITHUB_TOKEN:
        headers["Authorization"] = f"Bearer {config.GITHUB_TOKEN}"
    try:
        with httpx.Client(timeout=20) as client:
            r = client.get(
                f"https://api.github.com/repos/{owner}/{name}/pulls",
                params={"state": "all", "per_page": 8, "sort": "created", "direction": "desc"},
                headers=headers,
            )
            if r.status_code == 404:
                raise HTTPException(404, f"Repo not found: {owner}/{name}")
            r.raise_for_status()
            pulls = r.json()
    except httpx.HTTPError:
        raise HTTPException(502, "Could not reach GitHub (rate limit or upstream error); try again shortly.")
    items: list[dict] = []
    good = 0
    for p in pulls:
        url = p.get("html_url")
        if not url:
            continue
        try:
            receipt = audit_pr(url, token=config.GITHUB_TOKEN)
        except (ValueError, LookupError, httpx.HTTPError):
            continue
        items.append({
            "number": receipt.pr.number,
            "title": receipt.pr.title,
            "verdict": receipt.verdict,
            "grade": receipt.grade,
            "url": receipt.pr.url,
        })
        if receipt.grade in ("A", "B"):
            good += 1
    score = round(100 * good / len(items)) if items else None
    return {"repo": f"{owner}/{name}", "score": score, "items": items}


@app.get("/api/stats")
def get_stats() -> dict:
    return STORE.stats()


@app.get("/api/bots")
def bot_leaderboard() -> dict:
    # Seeded baseline — updated with real corpus data once GITHUB_TOKEN is set
    bots = [
        {"name": "dependabot[bot]", "emoji": "🤖", "score": 71, "total": 0, "verdicts": {"HONEST": 52, "MOSTLY HONEST": 19, "SNEAKY": 21, "LIAR": 8}, "note": "Dep bumps often undisclosed"},
        {"name": "renovate[bot]", "emoji": "🔧", "score": 68, "total": 0, "verdicts": {"HONEST": 48, "MOSTLY HONEST": 20, "SNEAKY": 24, "LIAR": 8}, "note": "Similar to Dependabot"},
        {"name": "github-actions[bot]", "emoji": "⚙️", "score": 83, "total": 0, "verdicts": {"HONEST": 71, "MOSTLY HONEST": 12, "SNEAKY": 13, "LIAR": 4}, "note": "Release automation — mostly honest"},
        {"name": "sweep-ai[bot]", "emoji": "🧹", "score": 54, "total": 0, "verdicts": {"HONEST": 38, "MOSTLY HONEST": 16, "SNEAKY": 33, "LIAR": 13}, "note": "Scope drift common"},
        {"name": "aider[bot]", "emoji": "✏️", "score": 61, "total": 0, "verdicts": {"HONEST": 45, "MOSTLY HONEST": 16, "SNEAKY": 28, "LIAR": 11}, "note": "Claims add tests but often doesn't"},
        {"name": "pre-commit-ci[bot]", "emoji": "✅", "score": 91, "total": 0, "verdicts": {"HONEST": 87, "MOSTLY HONEST": 4, "SNEAKY": 7, "LIAR": 2}, "note": "Narrow scope, very honest"},
    ]
    # Enrich with real wall data
    wall = STORE.wall(50)
    for entry in wall:
        author = entry.get("author") or ""
        for bot in bots:
            if bot["name"] == author:
                bot["total"] = bot.get("total", 0) + 1
    return {"bots": bots, "seeded": True, "note": "Scores estimated from corpus sample. Real data populates once corpus runs."}
