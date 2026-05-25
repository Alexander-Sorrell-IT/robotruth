# RoboTruth — Submission

> **Did the robot lie?**
> Paste a public GitHub PR. Get a receipt of what it *claimed* vs what it *actually did* — every sneaky, unrequested, or dangerous change cited at `file:line`. Deterministic. No AI in the verdict path.

**Try it:** https://robotruth-rdft.vercel.app
**Repo:** github.com/Alexander-Sorrell-IT/robotruth
**Contest:** Mind the Product — World Product Day 2026, *Everyone Ships Now*
**Builder:** Alexander Sorrell

---

## What

In 2026, most PRs are written by agents — Cursor, Claude Code, Copilot, Lovable, Dependabot. The PR description is the agent's *own narration*. Nobody can quickly answer the question every reviewer is silently asking: **did it only do what it said, or did it quietly do more?**

RoboTruth reads the diff and answers the question.

Paste a PR URL → in seconds you get a **receipt** with:

- A one-word **verdict** (`HONEST` / `MOSTLY HONEST` / `SNEAKY` / `LIAR`) and a letter grade `A`–`F`.
- Three buckets — **Delivered** (claimed and did), **Undisclosed** (did but didn't mention — the headline catch), **Unhonored** (claimed but missing).
- Every flag cites the file and line of the evidence.
- A footer that names the constraint: *"Deterministic. Every flag cites file:line. No AI opinions."*
- A shareable link whose OpenGraph preview *is* the verdict — so when it lands in Slack/X/LinkedIn it's already self-explanatory.

Beyond the receipt:

- **Wall of Shame** — global feed of the sneakiest caught bot-authored PRs.
- **Per-repo scorecard** — `/repo/{owner}/{name}` audits the recent PRs of any public repo on demand and emits an honesty score.
- **MCP server** — `pip install` a stdio MCP server that exposes `audit_pr` to Claude Code / Cursor / Cline. The agent audits the PR it just opened. Self-incrimination, in-workflow.

## Who it's for

Engineering leads, PMs, and solo builders who merge agent-authored PRs every day and have no fast way to verify them. The pain is felt weekly. The cost of *not* checking is unknown until it isn't.

## How it works (the part judges care about)

The verdict path is **deterministic on purpose.** LLMs do not decide. The pipeline:

1. **Ingest** — public GitHub REST API for PR title, body, and unified diff.
2. **Claim extraction** *(heuristic, labeled as such)* — regex over the human-written lead of the PR body (we cut off auto-generated changelogs, release-note tables, and HTML noise). Surfaces four claim kinds: `adds_tests`, `no_deps`, `no_breaking`, `scope_only`. The UI **shows the parsed claims back to the user**, editable — so a bad parse is fixed before it's shared, and the "how do you know what it claimed" objection is defused live.
3. **Deterministic scanners** — `dangerous_primitives`, `dependencies`, `scope_drift`, `security_guard`. Each emits flags with file, line, severity, and the literal evidence.
4. **Claim verification** — splits parsed claims into *delivered* vs *unhonored*.
5. **Grade** — pure function. Critical=3, moderate=1, minor=0. ≥2 critical → F. 1 critical → D. Else by score: 0=A, 1=B, ≤3=C, else D. Verdict word maps off the grade. The math is shown to the user: *"D: 1 undisclosed (1 critical), 0 unhonored; score=3"* — fully decomposable.

The same engine is imported by the web app (FastAPI on Vercel Python functions), the MCP server, the per-repo fan-out, and the upcoming CLI. No adapter contains audit logic.

## Tools used

- **Engine:** Python — `httpx`, `pydantic`, `unidiff`. No ML libraries. ~460 lines.
- **API:** FastAPI on Vercel Python serverless functions. Redis (Vercel KV / Upstash, auto-detected) for durable receipts and Wall storage; FileStore fallback.
- **Frontend:** Next.js 16 (App Router) on Vercel. Receipt page renders an OG image so shared links preview the catch.
- **MCP:** Python MCP SDK, stdio transport, packaged for `pip install`.
- **Verification:** Playwright against production — paste PR → live API call → DOM assertion on verdict, zero console errors.
- **Build copilot:** Claude Code (Opus 4.7). Every architectural call — engine-vs-API split, deterministic verdict path, claim editor UI as precision insurance, MCP-as-distribution, Wall attribution policy (bots only / humans anonymized) — was worked through with the assistant. The submission you are reading is itself co-authored with it.
- **Analytics:** Novus instruments the funnel: `landing_view → pr_pasted | example_clicked → receipt_generated → receipt_shared | image_copied → wall_view → submitted_to_wall`.

## What I learned

**The hero is the receipt, not the engine.** The catch only matters if it travels. I spent disproportionate time on the OG share image and the receipt's visual density — because a shared link in Slack already showing "LIAR · F" is the entire growth loop. The engine could be a thousand times more clever and it wouldn't matter without that.

**Determinism is a feature, not a constraint.** It would have been faster to ship an LLM judging the diff. I didn't, and the brand is the better for it. The line *"no AI in the verdict path"* answers more judge questions in one sentence than any architecture diagram could.

**Precision beats recall when your brand is honesty.** A false "Caught!" on an honest PR would be brand-fatal. I tuned for silence over noise: if the diff doesn't *unambiguously* prove the flag, I don't raise it. The claim editor (let users correct the parse before sharing) is precision insurance you can't get from tuning alone.

**Show your math.** Every flag cites `file:line`. The grade exposes its decomposition. The receipt footer names the methodology. People trust what they can audit.

**Build the same engine into every surface.** Web app, MCP, per-repo, CLI — all four import the same `audit_pr`. The MCP server was a weekend's work because it had no logic of its own.

## What's next

- Languages beyond JS/TS/Python.
- A robot-checked badge for repos that pass a moving honesty bar.
- A browser extension that injects the receipt straight into the GitHub PR page.
- A `pip install robotruth` CLI for local pre-merge auditing.
- Persistent per-repo dashboards with webhooks for teams that want the receipt on every PR.

---

*Built greenfield May 20 – June 20, 2026, for Mind the Product's World Product Day 2026 hackathon.*
