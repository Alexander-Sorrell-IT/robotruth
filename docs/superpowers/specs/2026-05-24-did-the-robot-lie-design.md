# RoboTruth — Design Spec
*("Did the robot lie?")*

**Status:** Draft for review · **Date:** 2026-05-24 · **Builder:** Alexander Sorrell
**Contest:** Mind the Product — *World Product Day 2026: Everyone Ships Now* · **Deadline:** June 20 2026 (treat 16:00 UTC / 11:00am CDT as the hard cutoff)

---

## 1. One-liner

**Paste a public GitHub PR URL → get a receipt showing what the PR *claimed* to do versus what it *actually* did — every sneaky, unrequested, or dangerous change flagged, file by line.**

Product name: **RoboTruth** — tagline ***"Did the robot lie?"*** Descriptor (analyst-facing): *AI PR Intent Receipt.* Claim `robotruth.dev`/`.ai` + npm/PyPI/GitHub org `robotruth` (all free; `.com` parked — skip).

## 2. Who it's for & the problem (Product Thinking)

In 2026 everyone ships AI-authored PRs (Cursor, Claude Code, Copilot, Lovable). The PR description is the agent's *own narration*. Nobody can quickly answer: **did it only do what it said — or did it quietly do more?** The pain is felt weekly by PMs, eng leads, and solo founders. The diff is the ground truth; we read it for you and produce a one-glance verdict.

This is the builder's signature edge made legible: he built an AI-governance system that **caught an agent bypassing user approval**. Same instinct, aimed at the one anxiety every judge feels.

## 3. Why this wins (rubric, 4×25%)

- **Product Thinking:** universal, currently-felt problem; crisp who/what/why.
- **Craft:** deterministic engine, every flag cites `file:line`, fail-loud, *no LLM in the verdict path*. The output is a polished, screenshot-bait receipt.
- **Originality & Ambition:** prior-art check found LLM PR *reviewers* and academic papers, but **no shipped product** doing "paste a PR URL → deterministic claims-vs-diff receipt." Wedge is open. MCP + per-repo add ambition.
- **Shippedness:** paste-a-URL (or browse the Wall) = value in 30s, no login; self-trafficking via shareable receipts; measurable via Novus.

**Does not compete with the sponsor:** Novus instruments *your* repo for product analytics; we audit *any public* PR for honesty. Complementary.

## 4. Hard constraints / eligibility

- NEW code, started on/after May 20 2026 (greenfield — satisfied).
- DEPLOYED public web app a stranger can use immediately (the web app is the hero / eligibility surface).
- GitHub repo with **Novus connected** (Novus instruments via GitHub, watches human traffic; dashboard screenshot required).
- Self-trafficking (shareable receipts + Wall of Shame + search demand).
- **Honesty note:** Novus sees the web app's *human* traffic only — **not** MCP tool-calls. The web app must carry the dashboard screenshot.

## 5. Architecture

```
                 audit_pr(url) → Receipt          ← CORE ENGINE (plain Python, NO AI)
                 ┌──────┬──────────┬───────────┬──────────┐
                 │      │          │           │          │
             web app   Wall +    MCP server   CLI/pip   direct
             (HERO)    per-repo  (devs)       (roadmap) import
             Novus-    (same engine fanned over many PRs)
             instrumented
```

**Commit day 1:** the engine is an importable module exposing `audit_pr(prUrl | rawDiff) → Receipt`. Web app = an HTTP route over it; MCP = a tool handler over it; per-repo = a fan-out over it. No adapter contains audit logic.

## 6. Core engine — `audit_pr()`

**Input:** a public GitHub PR URL, **or** a raw unified diff (fallback, Feature D).

**Pipeline (all deterministic except claim extraction, which is transparent heuristics):**

1. **Ingest:** fetch PR title + body + unified diff via public GitHub REST API (`/repos/{o}/{r}/pulls/{n}` + diff media type). No auth for public PRs. Fail-loud on 404/private/rate-limit → surface a clear message + offer the paste-a-diff path.
2. **Claim extraction (heuristic, labeled as such):** parse title/body into asserted intents:
   - promised actions ("added tests", "no breaking changes", "only touches X", "bumped Y")
   - scope words ("just", "only", "minor", named files/dirs)
   - domain map (e.g., title mentions "dark mode" → expected dirs ~ UI/theme; touching `auth/*` is unexpected)
3. **Deterministic diff scanners** (start: JS/TS + Python — covers the AI-tooling majority):
   - **Security-guard removal/weakening** (critical): removed/edited lines matching auth/authz/CSRF/CORS patterns, removed middleware/permission checks.
   - **Secret/env exposure** (critical): new secret-like literals, environment values newly logged or returned, `.env` committed.
   - **Dangerous primitives added** (critical): newly introduced dynamic code-evaluation, child-process / shell-spawning, or unsafe-deserialization calls (the classic remote-code-execution sinks).
   - **New outbound network** (critical/moderate): added HTTP-client calls (`fetch`/`axios`/`requests`) to new hosts.
   - **Dependency changes** (moderate): adds/bumps in `package.json`/`requirements.txt`/`pyproject` + lockfile movement.
   - **Test/CI disabled** (moderate): edits to `.github/workflows`, test config, skipped tests, deleted test files.
   - **Scope drift** (moderate): files changed outside dirs implied by the claim.
   - **`.gitignore`/lockfile surprises** (moderate/minor).
   - **Claim-not-honored** (varies): "added tests" → 0 test files; "no deps" → lockfile moved; "only X" → touched Y.
4. **Grade (deterministic given flags):** start at **A**; subtract by severity of *undisclosed* changes + *unhonored* claims. **F** = contradiction (claimed the opposite of what the diff does). Fully decomposable ("D — 1 critical + 2 moderate undisclosed; 1 unhonored claim").

**Output — `Receipt` object:**
```
Receipt {
  pr: { repo, number, title, url, author? }
  verdict: "HONEST" | "MOSTLY HONEST" | "SNEAKY" | "LIAR"   // Feature C word
  grade:   "A" | "B" | "C" | "D" | "F"
  buckets: {
    delivered:   Flag[]   // claimed & delivered
    undisclosed: Flag[]   // did, but didn't mention  (the headline catch)
    unhonored:   Flag[]   // claimed, but not found
  }
  math: string            // grade decomposition
}
Flag { label, file, line, severity, evidence }
```

## 7. The Receipt artifact (Feature C)

One shareable card: big **verdict word + letter grade**, three buckets (delivered / undisclosed / unhonored), every flag citing `file:line`, footer *"Deterministic. Every flag cites file:line. No AI opinions."* Actions: **Copy image · Share link · Audit your PR.** (Mockup lives in the brainstorm thread; final visual TBD in build.)

## 8. Web app (the HERO)

Next.js. Routes = the Novus funnel:
- `/` landing — headline + single input (PR URL) + pre-filled **juicy example PRs** (one-click) + the Wall preview. No login.
- `/r/[receiptId]` — a rendered receipt (shareable; has the OG image).
- `/wall` — global Wall of Shame (Feature B).
- `/repo/[owner]/[name]` — light per-repo scorecard (tier-2).
- `/api/audit` — calls `audit_pr`.
- **Paste-a-diff fallback (Feature D):** if GitHub fails/private/rate-limited, accept a pasted diff so the user never dead-ends.

## 9. Wall of Shame + light per-repo (Feature B + tier-2)

- **Global Wall:** browsable, ranked feed of the sneakiest caught PRs. Zero-input value (judge lands → instantly gets it). Seeded with 30+ real catches before launch. Opt-in submission from receipts. Generates the browsable *human* traffic Novus needs.
- **Light per-repo scorecard:** enter `owner/repo` → audit its recent PRs on demand → per-repo Wall + honesty score. Same engine fanned out. **No accounts, no DB-of-record, public repos only.** Shareable ("your repo's honesty score").

## 10. Share / OG image (Feature A)

Every receipt link renders the receipt card as its **OpenGraph/link-preview image** (dynamic image generation). A shared link in X/LinkedIn/Slack *shows the catch* in the preview → billboard → click-through. Directly attacks the #1 risk (empty Novus dashboard).

## 11. MCP server (Feature 5 / distribution)

A Python package (PyPI) exposing one MCP tool via the Python MCP SDK: `audit_pr(url | diff) → Receipt` (returns structured receipt + a link back to the web receipt page). Devs add it to Claude Code/Cursor/Cline; their agent audits the PR it just opened — self-incrimination in-workflow. **Not tracked by Novus** (acceptable; it's an Originality/distribution play). Demo beat: agent opens PR → MCP catches it lying → receipt inline.

## 12. Novus instrumentation

Event funnel: `landing_view → pr_pasted | example_clicked → receipt_generated → receipt_shared | image_copied → wall_view → submitted_to_wall`. Activation event = `receipt_generated`; the share loop (`receipt_generated → receipt_shared`) is the self-traffic proof. The required screenshot tells a *funnel story*, not a hit count.

## 13. Precision & testing (credibility = the whole game)

- Curated corpus of **20–30 real AI-generated PRs** (open-source repos are full of bot PRs) as the test set; tune **precision over recall** — only flag what the diff *unambiguously* proves.
- Every flag must cite `file:line` + the exact claim it contradicts, so even a borderline flag is self-evidently true, never an opinion.
- A false "Caught!" on an honest PR is brand-fatal → bias to silence over noise.
- Engine unit-tested against the corpus; grade rubric is pure-function tested.

## 14. Tech stack & deployment

- **Frontend:** Next.js (React, TS) — landing, receipt, Wall, per-repo views + a thin API proxy. Dynamic OG images via Vercel OG.
- **Engine (DECIDED):** **Python** package `audit_pr` (the core, NO AI) = single source of truth. Exposed to the web via FastAPI, deployable as **Vercel Python serverless functions** in the same repo (fallback: a small Railway/Render service). The same package powers the **MCP server (Python MCP SDK → PyPI)** and the future **pip** distribution. Chosen over TS-only specifically to unlock the reusable Python toolkit + Python MCP + pip surfaces.
- **Vercel** free tier → public URL (+ optional custom domain).
- **GitHub repo** (required for Novus). **Novus** connected to the repo.

## 15. Build sequence (28 days, cut from the bottom)

```
1. THE CATCH      engine + GitHub ingest + scanners + receipt render + corpus tuning   (70% of win)
2. THE SPREAD     OG/share image + verdict word (A+C)
3. THE FRONT DOOR global Wall of Shame (B), seeded
   -- all of #1-3 judge-ready by DAY 21 --
4. THE DEPTH      light per-repo scorecard
5. THE FLEX       MCP server
   -- cut below this line if time slips; #1-3 NEVER cut --
6. ROADMAP        heavy per-repo, CLI/pip, browser extension (a demo slide, not built)
```
Final week: polish copy, seed 30+ Wall receipts, soft-launch for **real traffic**, record the 2–3 min demo (test both an MCP-in and MCP-out cut).

## 16. Risks & mitigations

1. **Empty Novus dashboard (top risk):** pre-filled example PR above the fold + irresistible OG image + seeded Wall + real soft-launch traffic.
2. **Scanner noise / false positives:** precision-over-recall, corpus tuning, every flag cites evidence.
3. **"No LLM" honesty nuance:** claim-*extraction* is heuristic; frame as "deterministic verdict + deterministic diff scanners + transparent claim heuristics." Neutralized in one line.
4. **Scope creep eating the hero:** the build queue + day-21 bar + cut-from-bottom.
5. **GitHub rate limits:** caching + paste-a-diff fallback.

## 17. Out of scope (roadmap)

Heavy per-repo (OAuth/webhooks/persistent dashboard/private repos), CLI/pip package, browser extension, repo "robot-checked" badges, languages beyond JS/TS + Python. All become the ambition/roadmap slide.

## 18. Open questions

- Product name: **RESOLVED — RoboTruth** (tagline "Did the robot lie?"). Chosen via adversarial tournament: cleanest ownership (npm/PyPI/GitHub org all free, no trademark conflict) + most legible to non-technical judges. Claim robotruth.dev/.ai + packages.
- Engine language: **RESOLVED — Python engine + TS/Next.js frontend** (web calls the Python engine over HTTP via FastAPI/Vercel Python functions; unlocks pip + Python MCP).
- Exact verdict-word thresholds (tune on corpus).

## 19. Implementation constraints (advisor checklist — fold into the plan, not the design)

1. **Claim extraction = #1 precision risk.** If the parser misreads a prose PR description, the "unhonored/contradiction" bucket is confidently wrong and the brand becomes the liar. Plan must: (a) dedicate explicit precision-tuning days vs. the corpus; (b) add a UI affordance that **shows the parsed claim back** ("we read your description as promising X, Y, Z — edit"), so users fix bad parses before sharing AND it defuses the eng-judge "how do you know what it claimed?" live. Highest-leverage UI addition.
2. **GitHub rate limits:** 60/hr unauthenticated, 5000/hr with a token. Route all fetches through a server-side **GitHub PAT** in env + cache results. Verify unauth access to `/pulls/{n}` + diff media type before plan-lock. Anon limit collapses with 2 simultaneous judges or any Wall/per-repo fan-out.
3. **Day-21 gate = testable criteria, not a queue.** Per tier-1 item, e.g.: engine ≥X catches across the 30-PR corpus with **0 false positives**; OG image renders on iMessage + LinkedIn + X; Wall has ≥30 seeded receipts with screenshot-worthy headlines.
4. **Wall attribution policy (named decision):** seeding real public PRs under "Caught/Sneaky" next to real author names is social-PR risk. Decide once: prefer **bot-authored PRs only** (`dependabot[bot]`, `copilot-pull-request-reviewer[bot]`, `cursor-bot`, etc.) + anonymize humans + opt-in for human-authored.
5. **Vercel Python caps:** ~10s execution + package-size limits on free/hobby. Big diffs may blow it. Do the worst-case-diff math before plan-lock and decide upfront: Vercel Python functions vs. a separate Railway/Render Python service. Don't leave it "either/or."
6. **Corpus sourcing = named queries**, not "repos are full of bot PRs": GitHub searches for PRs by `dependabot[bot]`, `copilot-pull-request-reviewer[bot]`, `cursor-bot[bot]`, `claude-bot`, etc. Builds the corpus in hours.
7. **Demo video = named multi-day workstream** (week 3, not 4): storyboard, shoot two cuts (MCP-in / MCP-out), pick by judge-legibility test.
8. **MCP transport = stdio** (pip install + user adds to MCP client config), not HTTP. Write it down.
