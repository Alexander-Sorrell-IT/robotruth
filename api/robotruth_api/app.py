from __future__ import annotations
from pathlib import Path
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


@app.get("/api/receipt/{rid}")
def get_receipt(rid: str) -> dict:
    r = STORE.get(rid)
    if r is None:
        raise HTTPException(404, "Receipt not found")
    return r
