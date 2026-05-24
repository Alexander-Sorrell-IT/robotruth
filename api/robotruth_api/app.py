from __future__ import annotations
from pathlib import Path
import httpx
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
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
    return _store_and_return(receipt.model_dump())


@app.post("/api/audit/diff")
def audit_paste(req: DiffReq) -> dict:
    if len(req.diff.encode("utf-8")) > config.DIFF_MAX_BYTES:
        raise HTTPException(413, "Diff too large; trim it or audit a smaller PR.")
    pr = PRMeta(repo=req.repo, number=req.number, title=req.title, url=req.url, body=req.body)
    receipt = audit_diff(pr, req.diff, keep_claim_kinds=req.keep_claim_kinds)
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


@app.get("/api/repo/{owner}/{name}")
def repo_scorecard(owner: str, name: str) -> dict:
    headers = {"Accept": "application/vnd.github+json", "User-Agent": "robotruth"}
    if config.GITHUB_TOKEN:
        headers["Authorization"] = f"Bearer {config.GITHUB_TOKEN}"
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
    score = round(100 * good / len(items)) if items else 0
    return {"repo": f"{owner}/{name}", "score": score, "items": items}
