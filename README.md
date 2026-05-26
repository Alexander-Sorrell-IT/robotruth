# RoboTruth

> **The Receipts Protocol — first surface: GitHub PRs.**
> *Did the robot lie?*
> AI is now doing the work. Receipts make it impossible to lie about what it did.
>
> Paste a public GitHub PR. In seconds, get a deterministic receipt — every divergence between what the AI *claimed* and what it *actually did*, cited at `file:line`. **No model in the verdict path.**

**Try it now:** **[robotruth-rdft.vercel.app](https://robotruth-rdft.vercel.app)**

[![Wall of Shame](https://img.shields.io/badge/wall%20of%20shame-live-red)](https://robotruth-rdft.vercel.app/wall)
[![API](https://img.shields.io/badge/api-online-brightgreen)](https://robotruth.vercel.app/api/health)

---

## What

There is now a measurable gap between what an AI agent says it did and what it actually did. Nobody is measuring it. That is the category RoboTruth opens — **The Receipts Protocol**.

Pull requests are the first surface where the gap is visible at file-and-line resolution. Tomorrow it's deployment agents, customer-comms agents, financial agents, ops agents. RoboTruth reads the diff and answers the one question every reviewer is silently asking: **did the robot do only what it said, or did it quietly do more?**

Paste a PR URL → get a **receipt** with:

- A one-word verdict (`HONEST` / `MOSTLY HONEST` / `SNEAKY` / `LIAR`) + letter grade `A`–`F`
- Three buckets — **Delivered**, **Undisclosed** (the headline catch), **Unhonored**
- Every flag cites the file and line of the evidence
- A shareable link whose OpenGraph preview *is* the verdict card

## Why it's different

The verdict path is **deterministic on purpose.** LLMs do not decide. Heuristics extract claims; deterministic scanners read the diff; a pure-function grader emits the letter grade. *"No AI in the verdict path"* answers more questions than an architecture diagram could.

## How it works

1. **Ingest** — public GitHub REST API for PR title, body, unified diff
2. **Claim extraction** (heuristic, labeled as such) — regex over the human-written lead of the PR body
3. **Deterministic scanners** — `dangerous_primitives`, `dependencies`, `scope_drift`, `security_guard`
4. **Claim verification** — splits claims into delivered vs unhonored
5. **Grade** — pure function. Critical=3, moderate=1, minor=0. ≥2 critical → F. 1 critical → D. Else by score: 0=A, 1=B, ≤3=C, else D.

The same engine is imported by the web app, the MCP server, the per-repo fan-out, and (soon) the CLI.

## Surfaces

- **Web** — [robotruth-rdft.vercel.app](https://robotruth-rdft.vercel.app) · paste any PR URL
- **Wall of Shame** — [`/wall`](https://robotruth-rdft.vercel.app/wall) · the sneakiest caught bot PRs, globally
- **Per-repo scorecard** — [`/repo/{owner}/{name}`](https://robotruth-rdft.vercel.app/repo/facebook/react) · audits the last 8 PRs of any public repo on demand
- **MCP server** — `mcp/` · `pip install` a stdio server that exposes `audit_pr` to Claude Code / Cursor / Cline. The agent audits the PR it just opened.
- **API** — [robotruth.vercel.app](https://robotruth.vercel.app/api/health) · `POST /api/audit`

## Repo layout

```
robotruth/   Python engine (pip-installable, src layout). The audit logic.
api/         FastAPI wrapper deployed as Vercel Python functions.
web/         Next.js 16 frontend.
mcp/         Python MCP stdio server exposing `audit_pr`.
docs/        Submission, demo script, plans, specs.
```

## Built for

[Mind the Product — World Product Day 2026: *Everyone Ships Now*](https://worldproductday.mindtheproduct.com).
Built greenfield May 20 – June 20, 2026.

**Full submission write-up:** [`docs/SUBMISSION.md`](docs/SUBMISSION.md)

---

*The Receipts Protocol · deterministic verdicts · no model in the verdict path.*

> *The robot doesn't get to write its own performance review.*
