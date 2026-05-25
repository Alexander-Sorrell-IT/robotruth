# RoboTruth

> **Did the robot lie?**
> Paste a public GitHub PR. Get a receipt of what it *claimed* vs what it *actually did* — every sneaky, unrequested, or dangerous change cited at `file:line`. **Deterministic. No AI in the verdict path.**

**Try it now:** **[robotruth-rdft.vercel.app](https://robotruth-rdft.vercel.app)**

[![Wall of Shame](https://img.shields.io/badge/wall%20of%20shame-live-red)](https://robotruth-rdft.vercel.app/wall)
[![API](https://img.shields.io/badge/api-online-brightgreen)](https://robotruth.vercel.app/api/health)

---

## What

In 2026, most pull requests are written by agents — Cursor, Claude Code, Copilot, Lovable, Dependabot. The PR description is the agent's *own narration*. Nobody can quickly answer: **did it only do what it said, or did it quietly do more?**

RoboTruth reads the diff and answers the question.

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

*Deterministic AI-PR auditing · no AI opinions.*
