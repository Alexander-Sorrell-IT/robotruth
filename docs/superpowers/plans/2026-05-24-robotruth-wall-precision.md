# RoboTruth Wall + Precision — Implementation Plan (Plan 3)

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development. Steps use checkbox (`- [ ]`).

**Goal:** Make the engine's claims trustworthy on real-world PRs (precision), guard it with a real bot-PR corpus, and add the two self-trafficking surfaces: a global **Wall of Shame** and a **light per-repo scorecard**.

**Architecture:** Builds on the done engine (`robotruth/`), API (`api/`), and web (`web/`). T1–T2 harden the engine (pure, TDD). T3–T4 add API endpoints + Next.js pages over the same `audit_*` functions. No new infra.

**Tech Stack:** unchanged (Python engine/FastAPI; Next.js 16). Working dirs as in Plan 2.

**Why now (from the live smoke test):** auditing a real dependabot PR produced a spurious `scope_only` claim because claim-extraction read the auto-generated changelog in the body. Harmless once (threshold protected it) but it WILL cause false flags → fix precision first. **Precision is the brand.**

**LOCKED (advisor):** Wall shows **bot-authored PRs by default**; human-authored entries are **anonymized** (no author handle) unless opt-in. Corpus = real PRs by `dependabot[bot]`, `copilot-pull-request-reviewer[bot]`, `cursor[bot]`, etc.

---

## Task 1: Claim-extraction precision — ignore auto-generated body content ✅ DONE (ac15a9a) — 47 engine tests pass

**Files:** modify `robotruth/src/robotruth/claims.py`; test `robotruth/tests/test_claims_precision.py`. Working dir `robotruth/` (`. .venv/bin/activate`).

- [ ] **Step 1: failing test** `tests/test_claims_precision.py`
```python
from robotruth.claims import extract_claims

DEPENDABOT_BODY = """Bumps katex from 0.16.44 to 0.16.47.
<details>
<summary>Release notes</summary>
<p>only closes a note when used on a new line</p>
<li>fix: add tests for the new path</li>
</details>
Dependabot will resolve any conflicts with this PR.
"""

def test_ignores_changelog_prose_in_body():
    # 'only' and 'tests' appear ONLY inside the auto-generated changelog -> no claims
    claims = extract_claims("chore(deps): bump katex", DEPENDABOT_BODY)
    assert claims == []

def test_keeps_human_lead_paragraph_claims():
    body = "Added tests for the toggle. Only touches settings.\n<details><summary>x</summary>noise</details>"
    kinds = {c.kind for c in extract_claims("Add dark mode", body)}
    assert "adds_tests" in kinds and "scope_only" in kinds
```
- [ ] **Step 2:** run → FAIL
- [ ] **Step 3:** edit `claims.py` — add a body sanitizer used before regex matching:
```python
import re as _re

_CUTOFF_RE = _re.compile(
    r"(?is)(<details>|#{1,6}\s*release notes|#{1,6}\s*changelog|"
    r"#{1,6}\s*commits|dependabot will resolve|signed-off-by:|"
    r"<!--|\[//\]:)"
)
_TAG_RE = _re.compile(r"<[^>]+>")


def _human_body(body: str) -> str:
    """Keep only the human-written lead of a PR body: cut at the first
    auto-generated/changelog marker, strip HTML tags."""
    if not body:
        return ""
    m = _CUTOFF_RE.search(body)
    lead = body[: m.start()] if m else body
    return _TAG_RE.sub(" ", lead)
```
Then in `extract_claims`, change `text = f"{title}\n{body or ''}"` to:
```python
    text = f"{title}\n{_human_body(body)}"
```
- [ ] **Step 4:** run `pytest -q` (new test + full suite) → PASS
- [ ] **Step 5:** commit `git -C /media/phantomcore/AI_DRIVE/hackathons/mind add robotruth && git -C /media/phantomcore/AI_DRIVE/hackathons/mind commit -m "fix(engine): claim extraction ignores auto-generated changelog/HTML body"`

---

## Task 2: Real bot-PR corpus + precision regression guard

**Files:** create `robotruth/tests/corpus/` (committed JSON fixtures) + `robotruth/tests/test_corpus.py` + a fetch helper `robotruth/scripts/fetch_corpus.py`. Working dir `robotruth/`.

- [ ] **Step 1: fetch helper** `scripts/fetch_corpus.py` — given a list of PR URLs, fetch each via `robotruth.github.fetch_pr` and write `tests/corpus/<repo>-<n>.json` = `{"pr": {...}, "diff": "..."}`. (Run manually once with `GITHUB_TOKEN` set to seed ~6 real bot PRs across dependabot/copilot/cursor; commit the JSON so the test is offline + deterministic.)
```python
import json, sys
from pathlib import Path
from robotruth.github import fetch_pr
from robotruth.urls import parse_pr_url

def main(urls: list[str]) -> None:
    out = Path(__file__).resolve().parent.parent / "tests" / "corpus"
    out.mkdir(parents=True, exist_ok=True)
    for u in urls:
        o, r, n = parse_pr_url(u)
        pr, diff = fetch_pr(o, r, n)
        (out / f"{r}-{n}.json").write_text(json.dumps({"pr": pr.model_dump(), "diff": diff}))
        print("wrote", r, n)

if __name__ == "__main__":
    main(sys.argv[1:])
```
- [ ] **Step 2: regression test** `tests/test_corpus.py` — audit every committed fixture; assert **no critical false positives** (the precision guard) and snapshot the verdict:
```python
import json
from pathlib import Path
import pytest
from robotruth.types import PRMeta
from robotruth.engine import audit_diff

CORPUS = sorted((Path(__file__).parent / "corpus").glob("*.json"))

@pytest.mark.parametrize("path", CORPUS, ids=lambda p: p.stem)
def test_corpus_no_unexpected_criticals(path):
    data = json.loads(path.read_text())
    r = audit_diff(PRMeta(**data["pr"]), data["diff"])
    # Dependency bumps must never be graded worse than B on a bot PR with no
    # security-relevant changes. Tighten per-fixture as the corpus grows.
    crit = [f for f in r.undisclosed if f.severity == "critical"]
    assert crit == [], f"{path.stem}: unexpected critical flags {[f.label for f in crit]}"
```
(If `CORPUS` is empty, the parametrize yields no tests — seed it via Step 1 before relying on it.)
- [ ] **Step 3:** seed ≥6 fixtures (run Step 1 with real bot-PR URLs), run `pytest -q tests/test_corpus.py` → PASS. Tune scanners/claims if a fixture trips a false critical.
- [ ] **Step 4:** commit `git -C ... add robotruth && git -C ... commit -m "test(engine): real bot-PR corpus + precision regression guard"`

---

## Task 3: Wall of Shame (API list + web page) ✅ DONE (api 30085eb, web 04cf49b) — api 7 tests pass, web builds

**Files:** modify `api/robotruth_api/store.py` (+ recent list), `api/robotruth_api/app.py` (append on audit + GET /api/wall); web `web/app/wall/page.tsx`. Working dirs `api/`, `web/`.

- [ ] **Step 1 (api): recent-list in store** — add to each store a capped recent list of summaries. Add to `FileStore`/`RedisStore` an `add_wall(entry: dict)` and `wall(limit=30) -> list[dict]`. FileStore: keep a `wall.json` list (prepend, cap 50). RedisStore: `LPUSH wall` + `LTRIM 0 49` + `LRANGE`.
- [ ] **Step 2 (api): append + endpoint** in `app.py`: after a receipt is created in `_store_and_return`, if `receipt["verdict"] in ("SNEAKY","LIAR")`, build a summary `{id, repo, number, title, verdict, grade, author}` and, **anonymizing non-bot authors** (`author = author if author and author.endswith("[bot]") else None`), call `STORE.add_wall(summary)`. Add `@app.get("/api/wall")` → `{"items": STORE.wall()}`.
- [ ] **Step 3 (api): test** — post a SNEAKY-producing diff, then GET /api/wall returns ≥1 item with no raw human author. `pytest -q` PASS. Commit.
- [ ] **Step 4 (web): page** `web/app/wall/page.tsx` (server component) — fetch `${BASE}/api/wall`, render a ranked list of cards linking to `/r/{id}` (repo #n · verdict · grade · title). `npm run build` PASS. Commit `feat: Wall of Shame (api list + /wall page, bot-anonymized)`.

---

## Task 4: Light per-repo scorecard (on-demand, public, no DB) ✅ DONE (api a87efec, web 468f255) — api 8 tests pass, web builds

**Files:** `api/robotruth_api/app.py` (GET /api/repo endpoint), web `web/app/repo/[owner]/[name]/page.tsx`. 

- [ ] **Step 1 (api):** add `@app.get("/api/repo/{owner}/{name}")` — list the repo's recent PRs via the public GitHub API (`/repos/{o}/{n}/pulls?state=all&per_page=10`), `audit_pr` each (reuse `config.GITHUB_TOKEN`, cap 10, skip any that error/404), return `{repo, score, items:[{number,title,verdict,grade}]}` where `score` = % graded A/B. Cap total work; fail-soft per PR.
- [ ] **Step 2 (api): test** — monkeypatch the PR-list fetch + `audit_pr` to return 2 fakes; assert score + items shape. `pytest -q` PASS. Commit.
- [ ] **Step 3 (web): page** `web/app/repo/[owner]/[name]/page.tsx` (server component, `params` is async) — fetch `${BASE}/api/repo/{owner}/{name}`, render the honesty score + the per-PR mini-list. `npm run build` PASS. Commit `feat: light per-repo honesty scorecard`.

---

## Self-Review (against spec §9, §13 + the live-smoke finding)
- T1 fixes the real changelog-prose claim bug (spec §13 precision; smoke-test finding). T2 = the corpus/precision guard (advisor #6) — **seed it with real bot PRs before trusting it**. T3 = Wall of Shame (spec §9, Feature B) with the advisor's bot-only/anonymize attribution (advisor #4). T4 = light per-repo (spec §9 tier-2), on-demand/public/no-DB as decided.
- Out of scope (correct): heavy per-repo, MCP (Plan 4), browser extension/badges (roadmap).
- Open: per-fixture verdict assertions in T2 tighten as the corpus grows; Wall enumeration uses a capped recent-list (KV has no scan) — acceptable for the hackathon.
