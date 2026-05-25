# RoboTruth Web Hero — Implementation Plan (Plan 2)

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development to implement task-by-task. Steps use checkbox (`- [ ]`).

**Goal:** A deployed web app where a stranger pastes a public GitHub PR URL and gets a shareable RoboTruth receipt (verdict + grade + buckets), in <30s, no login.

**Architecture:** FastAPI service wraps the existing `robotruth` engine (`audit_pr`/`audit_diff`) → JSON `Receipt`. Receipts are persisted by id in a `ReceiptStore` (file-backed in dev, Vercel KV / Upstash Redis in prod) so `/r/[id]` and the OG image are stable snapshots. Next.js (TS) frontend calls the API, renders the receipt card, generates the OG share image, and offers a paste-a-diff fallback + a claims edit→re-audit affordance. Deploy-agnostic: runs fully locally; deploys to Vercel (Next.js) + a Python target (Vercel Python function or Railway) decided at the deploy step.

**Tech Stack:** Python 3.11 + FastAPI + uvicorn (API); Next.js 14 (App Router, TS) + `@vercel/og` (frontend); Upstash Redis / Vercel KV (prod store).

**Working directory:** repo root `/media/phantomcore/AI_DRIVE/hackathons/mind/` (monorepo). API in `api/`, frontend in `web/`, engine in `robotruth/` (done). Run commands from each subdir as noted.

**LOCKED DECISIONS (from advisor):**
1. API imports the engine via `requirements.txt` → `robotruth @ git+https://github.com/<OWNER>/robotruth@<sha>` in prod; in dev, `pip install -e ../robotruth`.
2. Persist receipts (Vercel KV/Upstash in prod); **never recompute** a shared receipt (force-push would flip the verdict).
3. GitHub + Vercel + Novus are USER ACTIONS (see end). Connect Novus as soon as the hero is deployed.
4. Diff-size cap ~1MB at fetch → route to paste-a-diff. Claims affordance wires the **edit→re-audit** path. Scope = paste→receipt→share ONLY (Wall/per-repo/MCP are Plans 3–4). Novus auto-instruments from the repo — do NOT hardcode event names.

---

## USER ACTION 0 — GitHub repo (do this whenever; unblocks prod deploy)
```bash
# in /media/phantomcore/AI_DRIVE/hackathons/mind
gh repo create robotruth --public --source=. --remote=origin --push
# (or: create an empty repo in the GitHub UI, then:)
# git remote add origin https://github.com/<you>/robotruth.git && git push -u origin main
```
Then note the repo URL — it goes into `api/requirements.txt` (decision 1) at deploy time.

---

## File Structure
```
api/
  pyproject.toml          # dev install (fastapi, uvicorn, robotruth path dep)
  requirements.txt        # prod deps (incl. robotruth git URL) — filled at deploy
  robotruth_api/
    __init__.py
    app.py                # FastAPI app + routes
    store.py              # ReceiptStore (file dev / redis prod), get/put by id
    config.py             # env: DIFF_MAX_BYTES, REDIS_URL, GITHUB_TOKEN
  tests/
    test_app.py  test_store.py
web/
  package.json  next.config.mjs  tsconfig.json
  lib/api.ts              # typed client -> API
  lib/receipt.ts          # Receipt TS type (mirror of engine Receipt)
  components/ReceiptCard.tsx
  app/page.tsx            # landing: input + examples + paste-diff
  app/r/[id]/page.tsx     # receipt page (reads persisted receipt)
  app/api/og/route.tsx    # OG image (@vercel/og)
  app/globals.css
```

---

## Task 1: FastAPI app skeleton + health
**Files:** create `api/pyproject.toml`, `api/robotruth_api/__init__.py`, `api/robotruth_api/config.py`, `api/robotruth_api/app.py`, `api/tests/test_app.py`

- [ ] **Step 1: failing test** `api/tests/test_app.py`
```python
from fastapi.testclient import TestClient
from robotruth_api.app import app

def test_health():
    c = TestClient(app)
    r = c.get("/api/health")
    assert r.status_code == 200 and r.json()["ok"] is True
```
- [ ] **Step 2:** `cd api && python -m venv .venv && . .venv/bin/activate && pip install -e ../robotruth && pip install fastapi "uvicorn[standard]" httpx pytest && pip install -e .` ; run `pytest -q` → FAIL (no app)
- [ ] **Step 3:** `api/pyproject.toml`
```toml
[project]
name = "robotruth-api"
version = "0.1.0"
requires-python = ">=3.11"
dependencies = ["fastapi>=0.115", "uvicorn[standard]>=0.30", "robotruth", "redis>=5"]
[project.optional-dependencies]
dev = ["pytest>=8", "httpx>=0.27"]
[build-system]
requires = ["setuptools>=68"]
build-backend = "setuptools.build_meta"
[tool.setuptools.packages.find]
where = ["."]
include = ["robotruth_api*"]
```
`api/robotruth_api/__init__.py`: `"""RoboTruth web API."""`
`api/robotruth_api/config.py`:
```python
from __future__ import annotations
import os

DIFF_MAX_BYTES = int(os.environ.get("DIFF_MAX_BYTES", str(1_000_000)))
REDIS_URL = os.environ.get("REDIS_URL")  # None => file-backed dev store
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")
```
`api/robotruth_api/app.py`:
```python
from __future__ import annotations
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="RoboTruth API")
app.add_middleware(
    CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"],
)


@app.get("/api/health")
def health() -> dict:
    return {"ok": True}
```
- [ ] **Step 4:** `pytest -q` → PASS
- [ ] **Step 5:** commit `git add api && git commit -m "feat(api): FastAPI skeleton + health"`

---

## Task 2: ReceiptStore (persist + fetch by id)
**Files:** create `api/robotruth_api/store.py`, `api/tests/test_store.py`

- [ ] **Step 1: failing test** `api/tests/test_store.py`
```python
from robotruth_api.store import FileStore

def test_put_get_roundtrip(tmp_path):
    s = FileStore(tmp_path)
    rid = s.put({"verdict": "LIAR", "grade": "F"})
    assert isinstance(rid, str) and len(rid) >= 6
    assert s.get(rid)["grade"] == "F"

def test_get_missing_returns_none(tmp_path):
    assert FileStore(tmp_path).get("nope") is None
```
- [ ] **Step 2:** `pytest -q tests/test_store.py` → FAIL
- [ ] **Step 3:** `api/robotruth_api/store.py`
```python
from __future__ import annotations
import json
import secrets
from pathlib import Path
from typing import Protocol


class ReceiptStore(Protocol):
    def put(self, receipt: dict) -> str: ...
    def get(self, rid: str) -> dict | None: ...


def _new_id() -> str:
    return secrets.token_urlsafe(6)


class FileStore:
    """Dev store: one JSON file per receipt under a directory."""

    def __init__(self, root: Path | str) -> None:
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)

    def put(self, receipt: dict) -> str:
        rid = _new_id()
        (self.root / f"{rid}.json").write_text(json.dumps(receipt))
        return rid

    def get(self, rid: str) -> dict | None:
        p = self.root / f"{rid}.json"
        if not p.exists():
            return None
        return json.loads(p.read_text())


class RedisStore:
    """Prod store: Upstash/Vercel KV via redis URL."""

    def __init__(self, url: str) -> None:
        import redis  # lazy
        self._r = redis.from_url(url, decode_responses=True)

    def put(self, receipt: dict) -> str:
        rid = _new_id()
        self._r.set(f"receipt:{rid}", json.dumps(receipt))
        return rid

    def get(self, rid: str) -> dict | None:
        raw = self._r.get(f"receipt:{rid}")
        return json.loads(raw) if raw else None
```
- [ ] **Step 4:** `pytest -q tests/test_store.py` → PASS
- [ ] **Step 5:** commit `git add api && git commit -m "feat(api): receipt store (file dev / redis prod)"`

---

## Task 3: Audit endpoints (URL + paste-diff) with diff cap + persistence
**Files:** modify `api/robotruth_api/app.py`, add tests to `api/tests/test_app.py`

- [ ] **Step 1: failing tests** (append to `test_app.py`)
```python
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
```
- [ ] **Step 2:** run → FAIL
- [ ] **Step 3:** rewrite `api/robotruth_api/app.py`
```python
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


class DiffReq(BaseModel):
    repo: str
    number: int
    title: str
    url: str
    body: str = ""
    diff: str


def _store_and_return(receipt: dict) -> dict:
    rid = STORE.put(receipt)
    return {"id": rid, "receipt": receipt}


@app.get("/api/health")
def health() -> dict:
    return {"ok": True}


@app.post("/api/audit")
def audit_url(req: UrlReq) -> dict:
    try:
        receipt = audit_pr(req.url, token=config.GITHUB_TOKEN)
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
    receipt = audit_diff(pr, req.diff)
    return _store_and_return(receipt.model_dump())


@app.get("/api/receipt/{rid}")
def get_receipt(rid: str) -> dict:
    r = STORE.get(rid)
    if r is None:
        raise HTTPException(404, "Receipt not found")
    return r
```
- [ ] **Step 4:** run full `pytest -q` → PASS
- [ ] **Step 5:** commit `git add api && git commit -m "feat(api): audit URL + paste-diff endpoints, persisted, diff-capped"`
- [ ] **Step 6 (smoke):** `uvicorn robotruth_api.app:app --port 8000` then `curl -s localhost:8000/api/audit -d '{"url":"<a real bot PR>"}' -H 'content-type: application/json' | head` → JSON with id + receipt.

---

## Task 4: Next.js scaffold + Receipt type + API client ✅ DONE (33109d6) — Next.js 16 (params is async)
**Files:** create `web/` (Next.js app), `web/lib/receipt.ts`, `web/lib/api.ts`

- [ ] **Step 1:** scaffold: `cd /media/phantomcore/AI_DRIVE/hackathons/mind && npx create-next-app@latest web --ts --app --eslint --no-tailwind --no-src-dir --import-alias "@/*"` (accept defaults). Then `cd web`.
- [ ] **Step 2:** `web/lib/receipt.ts` (mirror engine Receipt)
```typescript
export type Severity = "critical" | "moderate" | "minor";
export type Verdict = "HONEST" | "MOSTLY HONEST" | "SNEAKY" | "LIAR";
export type Grade = "A" | "B" | "C" | "D" | "F";
export interface Flag { label: string; file: string; line: number | null; severity: Severity; evidence: string; }
export interface Receipt {
  pr: { repo: string; number: number; title: string; url: string; body?: string; author?: string | null };
  verdict: Verdict; grade: Grade;
  delivered: Flag[]; undisclosed: Flag[]; unhonored: Flag[];
  parsed_claims: string[]; math: string;
}
```
- [ ] **Step 3:** `web/lib/api.ts`
```typescript
import type { Receipt } from "./receipt";
const BASE = process.env.NEXT_PUBLIC_API_BASE ?? "http://localhost:8000";

export async function auditUrl(url: string): Promise<{ id: string; receipt: Receipt }> {
  const r = await fetch(`${BASE}/api/audit`, {
    method: "POST", headers: { "content-type": "application/json" }, body: JSON.stringify({ url }),
  });
  if (!r.ok) throw new Error((await r.json().catch(() => ({}))).detail ?? `Audit failed (${r.status})`);
  return r.json();
}

export async function getReceipt(id: string): Promise<Receipt> {
  const r = await fetch(`${BASE}/api/receipt/${id}`, { cache: "no-store" });
  if (!r.ok) throw new Error("Receipt not found");
  return r.json();
}
```
- [ ] **Step 4:** verify `npm run build` compiles (after page exists in Task 5) — for now `npx tsc --noEmit` passes for these libs.
- [ ] **Step 5:** commit `git add web && git commit -m "feat(web): Next.js scaffold + Receipt type + API client"`

---

## Task 5: Receipt card component + receipt page ✅ DONE (35f2a8d)
**Files:** create `web/components/ReceiptCard.tsx`, `web/app/r/[id]/page.tsx`

- [ ] **Step 1:** `web/components/ReceiptCard.tsx`
```tsx
import type { Receipt, Flag } from "@/lib/receipt";

const VERDICT_COLOR: Record<string, string> = {
  HONEST: "#16a34a", "MOSTLY HONEST": "#65a30d", SNEAKY: "#ea580c", LIAR: "#dc2626",
};

function Bucket({ title, icon, flags }: { title: string; icon: string; flags: Flag[] }) {
  if (flags.length === 0) return null;
  return (
    <div style={{ marginTop: 16 }}>
      <h3 style={{ margin: 0, fontSize: 14, textTransform: "uppercase", letterSpacing: 1 }}>{icon} {title}</h3>
      <ul style={{ margin: "6px 0 0", paddingLeft: 18 }}>
        {flags.map((f, i) => (
          <li key={i} style={{ marginBottom: 4 }}>
            {f.label}{f.file ? ` — ${f.file}${f.line ? `:${f.line}` : ""}` : ""}
          </li>
        ))}
      </ul>
    </div>
  );
}

export function ReceiptCard({ receipt }: { receipt: Receipt }) {
  const c = VERDICT_COLOR[receipt.verdict] ?? "#444";
  return (
    <div style={{ maxWidth: 640, margin: "0 auto", border: "1px solid #e5e7eb", borderRadius: 12, padding: 24, fontFamily: "ui-sans-serif, system-ui" }}>
      <div style={{ fontSize: 12, color: "#6b7280" }}>INTENT RECEIPT · {receipt.pr.repo} #{receipt.pr.number}</div>
      <div style={{ fontSize: 16, fontWeight: 600, marginTop: 4 }}>{receipt.pr.title}</div>
      <div style={{ display: "flex", alignItems: "baseline", gap: 12, marginTop: 16 }}>
        <span style={{ fontSize: 34, fontWeight: 800, color: c }}>{receipt.verdict}</span>
        <span style={{ fontSize: 22, fontWeight: 700, color: c }}>{receipt.grade}</span>
      </div>
      <Bucket title="Did, but didn't mention" icon="⚠️" flags={receipt.undisclosed} />
      <Bucket title="Claimed, but not found" icon="❌" flags={receipt.unhonored} />
      <Bucket title="Claimed & delivered" icon="✅" flags={receipt.delivered} />
      <div style={{ marginTop: 16, fontSize: 11, color: "#9ca3af" }}>
        Deterministic. Every flag cites file:line. No AI opinions. — {receipt.math}
      </div>
    </div>
  );
}
```
- [ ] **Step 2:** `web/app/r/[id]/page.tsx`
```tsx
import { getReceipt } from "@/lib/api";
import { ReceiptCard } from "@/components/ReceiptCard";

export default async function ReceiptPage({ params }: { params: { id: string } }) {
  let receipt;
  try { receipt = await getReceipt(params.id); }
  catch { return <main style={{ padding: 40 }}>Receipt not found.</main>; }
  return (
    <main style={{ padding: "40px 16px" }}>
      <ReceiptCard receipt={receipt} />
      <p style={{ textAlign: "center", marginTop: 24 }}><a href="/">Audit your own PR →</a></p>
    </main>
  );
}
```
- [ ] **Step 3:** `npm run build` compiles.
- [ ] **Step 4:** commit `git add web && git commit -m "feat(web): receipt card + receipt page"`

---

## Task 6: Landing page — input, examples, paste-diff ✅ DONE (c1872b8)
**Files:** create `web/app/page.tsx` (client component)

- [ ] **Step 1:** `web/app/page.tsx`
```tsx
"use client";
import { useState } from "react";
import { useRouter } from "next/navigation";
import { auditUrl } from "@/lib/api";

const EXAMPLES = [
  "https://github.com/<seed-bot-pr-1>",
  "https://github.com/<seed-bot-pr-2>",
];

export default function Home() {
  const [url, setUrl] = useState("");
  const [busy, setBusy] = useState(false);
  const [err, setErr] = useState("");
  const router = useRouter();

  async function run(target: string) {
    setBusy(true); setErr("");
    try { const { id } = await auditUrl(target); router.push(`/r/${id}`); }
    catch (e) { setErr((e as Error).message); } finally { setBusy(false); }
  }

  return (
    <main style={{ maxWidth: 640, margin: "0 auto", padding: "64px 16px", fontFamily: "ui-sans-serif, system-ui" }}>
      <h1 style={{ fontSize: 34, fontWeight: 800 }}>Did the robot lie?</h1>
      <p style={{ color: "#4b5563" }}>Paste a public GitHub PR. See what it <em>claimed</em> vs. what it <em>actually did</em>.</p>
      <form onSubmit={(e) => { e.preventDefault(); if (url) run(url); }} style={{ display: "flex", gap: 8, marginTop: 16 }}>
        <input value={url} onChange={(e) => setUrl(e.target.value)} placeholder="Paste a public GitHub PR link"
               style={{ flex: 1, padding: 12, border: "1px solid #d1d5db", borderRadius: 8 }} />
        <button disabled={busy} style={{ padding: "12px 18px", borderRadius: 8, background: "#111827", color: "#fff", border: 0 }}>
          {busy ? "Reading…" : "Audit"}
        </button>
      </form>
      {err && <p style={{ color: "#dc2626" }}>{err}</p>}
      <p style={{ marginTop: 16, color: "#6b7280" }}>Try one:{" "}
        {EXAMPLES.map((e, i) => (
          <button key={i} onClick={() => run(e)} disabled={busy}
                  style={{ marginRight: 8, textDecoration: "underline", background: "none", border: 0, cursor: "pointer", color: "#2563eb" }}>
            example {i + 1}
          </button>
        ))}
      </p>
    </main>
  );
}
```
- [ ] **Step 2:** Replace the example URLs with 2 real bot PRs once known (Plan 3 seeds the full set). `npm run build` compiles.
- [ ] **Step 3:** smoke: run API (`uvicorn` on :8000) + `npm run dev`, paste a real PR URL → redirected to `/r/[id]` showing the receipt.
- [ ] **Step 4:** commit `git add web && git commit -m "feat(web): landing page with audit + examples"`

---

## Task 7: OG share image ✅ DONE (4d85569) — ⚠️ MUST set `metadataBase` (root layout) to the prod URL at deploy, else OG image URLs resolve to localhost and social previews break. Verified live: OG route returns PNG 1200×630.
**Files:** create `web/app/api/og/route.tsx`; modify `web/app/r/[id]/page.tsx` to set OG metadata

- [ ] **Step 1:** `npm i @vercel/og` (or use built-in `next/og` ImageResponse).
- [ ] **Step 2:** `web/app/api/og/route.tsx` — render verdict+grade+repo from query (`?id=` → fetch receipt, or pass `verdict/grade/title` as params). Use `ImageResponse` from `next/og`. (Reads the persisted receipt by id for accuracy.)
- [ ] **Step 3:** in `web/app/r/[id]/page.tsx`, export `generateMetadata({ params })` that fetches the receipt and sets `openGraph.images` to `/api/og?id=<id>` and a punchy title/description ("<verdict> · grade <grade> · <repo> #<n>").
- [ ] **Step 4:** verify the OG route returns an image locally (`curl localhost:3000/api/og?id=<id> -o og.png`) and the receipt page `<head>` has `og:image`.
- [ ] **Step 5:** commit `git add web && git commit -m "feat(web): dynamic OG share image for receipts"`

---

## Task 8: Claims edit → re-audit affordance ✅ DONE (engine af6ca30, api 41e225f, web aa10ccc) — PLAN 2 BUILD COMPLETE (deploy = user actions)
**Files:** modify `web/components/ReceiptCard.tsx` (show parsed_claims with an edit control) + a re-audit path

- [ ] **Step 1:** Display `parsed_claims` as "We read this PR as promising: …" with an **Edit** toggle that lets the user remove a mis-parsed claim, then re-submit to `/api/audit/diff` (or a new `/api/audit/recompute` taking pr meta + diff + overridden claims). Keep it minimal: the edit removes a claim and re-renders the (recomputed) receipt.
- [ ] **Step 2:** Add API support: `POST /api/audit/recompute` accepting pr meta + diff + `claims_override: list[str]` (claim kinds to keep), wiring through `audit_diff` with a claims filter. (Add a small `claim_kinds` param to `audit_diff` or a thin wrapper.) Test it in `api/tests/test_app.py`.
- [ ] **Step 3:** `npm run build` + `pytest -q` pass.
- [ ] **Step 4:** commit `git add api web && git commit -m "feat: show parsed claims with edit->re-audit (credibility affordance)"`

---

## USER ACTION (DEPLOY) — when the hero works locally
**The 15-min deploy spike comes first** (verify the model before relying on it):
1. **GitHub:** ensure USER ACTION 0 is done; put the repo URL + latest engine SHA into `api/requirements.txt` as `robotruth @ git+https://github.com/<you>/robotruth@<sha>`.
2. **Spike:** deploy a *trivial* `web/` to Vercel (`vercel`) and confirm it serves. Then decide the API target:
   - **Vercel Python function:** add `api/index.py` exposing the FastAPI `app` via the ASGI handler + `vercel.json` routing `/api/*` to it; redeploy; hit `/api/health`.
   - **If painful → Railway:** `railway up` the `api/` FastAPI; set `web` env `NEXT_PUBLIC_API_BASE` to the Railway URL.
3. **KV:** create Vercel KV (or Upstash Redis); set `REDIS_URL` on the API; redeploy.
4. **Env:** set `GITHUB_TOKEN` (a fine-scoped PAT, public_repo read) on the API for the 5000/hr rate limit.
5. **Novus:** connect Novus to the GitHub repo; deploy; confirm the dashboard sees the app. Then drive real traffic (share receipts) and screenshot near submission.

---

## Self-Review (against spec §8–12)
- Covers: paste-URL audit (T3) · paste-diff fallback + diff cap (T3) · persisted stable receipts (T2/T3) · receipt card with verdict+grade+buckets (T5) · landing + examples (T6) · OG share image (T7) · claims edit→re-audit (T8) · engine reuse via FastAPI (T1/T3). Deploy + Novus = user actions. Wall/per-repo/MCP = Plans 3/4 (out of scope here, correctly).
- No placeholders except the 2 example PR URLs (filled when real bot PRs are chosen — Plan 3 seeds the full set).
- Types: `Receipt`/`Flag` TS mirror matches engine `model_dump()` keys (snake_case: parsed_claims, etc.).
