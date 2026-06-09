# Devpost form — paste-ready fields

Paste each block into the matching Devpost field. All copy is lifted from `docs/SUBMISSION.md`
(no new claims). Field names below are Devpost's standard project-submission fields; if the live
form differs, map by intent. The four RULE-REQUIRED materials are marked **[REQUIRED]**.

> Before you submit, confirm against `mindtheproduct.devpost.com/rules`. Required materials:
> (1) public app URL, (2) demo video on **YouTube / Vimeo / Youku** (NOT Loom), (3) Novus.ai
> dashboard screenshot, (4) text description. Items 1–4 are all that the rules mandate.

---

## Project name
RoboTruth

## Elevator pitch / tagline (~200 chars)
Deterministic, cite-by-cite receipts for what an AI agent claimed vs. what it actually did — issued by a system that contains no AI. Paste a public GitHub PR, get a verdict graded at file:line.

## [REQUIRED] Try it — public app URL
https://robotruth-rdft.vercel.app

## Repository
https://github.com/Alexander-Sorrell-IT/robotruth

## [REQUIRED] Demo video URL
https://youtu.be/ccVobX4Qj4c
(Uploaded to YouTube as Unlisted on 2026-06-09 — the 2:36 cut, narrated in the cloned voice.
Switch to Public once everything's verified. NOT Loom.)

---

## Inspiration
There is now a measurable gap between what an AI agent says it did and what it actually did, and nobody is measuring it. Every era of automation eventually gets its accountability layer: finance got double-entry bookkeeping once ledgers got fast enough to lie; the web got HTTPS once traffic was worth intercepting; software supply chains got SBOMs once dependencies started shipping malware. AI agents now write the code that ships to production — and the only record of their intent is a paragraph the agent wrote about itself. In May 2026 a large, fast-growing share of PRs on active repos are agent-authored; the PR description is now an unaudited claim by a non-human author with no reputational skin in the game.

## What it does
RoboTruth issues a deterministic, cite-by-cite record of what an AI agent claimed versus what it actually did — the first product in The Receipts Protocol. Paste a public GitHub PR and in seconds you get a **receipt**: a verdict word, a letter grade, three buckets (Delivered / Undisclosed / Unhonored), and every undisclosed change cited at `file:line`, with the grade math decomposed on screen. No model sits in the verdict path — the robot doesn't grade its own homework. The engine is precision-biased: it never accuses, it cites; claims it can't verify surface as *unverified*, not as lies. The same engine fans out to a public Wall of Shame, a per-repo scorecard, an MCP server (`audit_pr` in Claude Code / Cursor / Cline), a GitHub Action that posts the verdict inline as a PR comment, and a Deploy Receipt preview.

## How we built it
One deterministic engine (~590 lines of Python — `httpx`, `pydantic`, `unidiff`, no ML libraries) is the single source of truth behind every surface. Pipeline: (1) ingest PR title, body, and unified diff via GitHub's public API; (2) extract claims with labeled-heuristic regex over the human-written lead, surfaced back as an *editable* claim list so a bad parse is corrected before sharing; (3) scan the diff with four deterministic passes — `dangerous_primitives`, `dependencies`, `scope_drift`, `security_guard` — each flag carrying file, line, severity, and literal evidence; (4) grade with a pure function whose decomposition is shown on the receipt. No adapter contains audit logic. Surfaces: Next.js 16 frontend on Vercel, FastAPI on Vercel Python functions, Upstash Redis durable receipts (file-backed fallback), Python MCP SDK stdio server. Verified by 88 pytest tests (73 engine + 13 API + 2 MCP) and TypeScript strict mode.

## Challenges we ran into
Keeping the verdict path deterministic was the hard brand call: shipping an LLM as the judge would have been faster and would have killed the product. Precision was the second: an accountability product that ever wrongly accuses an honest PR is no longer one, so false positives are the failure mode we refuse and false negatives are the one we own and disclose — every flag had to carry the literal evidence the regex matched so a reader can audit the auditor.

## Accomplishments that we're proud of
A single ~590-line engine with no ML libraries powering the web API, MCP server, per-repo scorecard, GitHub Action, and CLI — the category lives in the function, not the surface. Novus's own AI independently scanned RoboTruth, reconstructed its personas, product areas, and user flows accurately, and re-derived the engine's top precision risk unprompted — third-party confirmation from the sponsor's own tooling.

## What we learned
Determinism is the brand — "No model in the verdict path" answers more judge questions in nine words than any diagram. Show your math or you're just another opinion: every flag cites `file:line`, the grade decomposes on screen, the footer names the methodology. An accountability product that can't itself be audited isn't one.

## What's next for RoboTruth
The next surfaces — deployment agents, customer-comms agents, financial agents, ops agents, scheduler agents — are already shipping work and narrating themselves. The measured share→submit cliff (receipts spread, evidence doesn't always follow them home) is the next thing to design for, not more scanners.

## Built With (tags)
python, fastapi, nextjs, typescript, vercel, redis, upstash, mcp, pydantic, httpx, github-api, claude

## [REQUIRED] Novus.ai dashboard screenshot
Attach: `submission_assets/novus_memory_product_model.png` (primary — shows the AI-reconstructed
product model). Supporting: `novus_aiagents.png`, `novus_pages_click_events.png`, `novus_visitors.png`.

## Cover / thumbnail image (if the form offers it — NOT rule-required)
No dedicated cover asset exists yet. Option: screenshot a live receipt card from
https://robotruth-rdft.vercel.app/wall (a SNEAKY catch reads best; HONEST card is the clean fallback).
