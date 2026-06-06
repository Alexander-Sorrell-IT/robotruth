# RoboTruth — Submission

**Try it:** https://robotruth-rdft.vercel.app
**Repo:** github.com/Alexander-Sorrell-IT/robotruth
**Contest:** Mind the Product — World Product Day 2026, *Everyone Ships Now*
**Builder:** Alexander Sorrell

---

There is now a measurable gap between what an AI agent says it did and what it actually did. **Nobody is measuring it.** That is the category RoboTruth opens.

Every era of automation eventually gets its accountability layer. Finance got double-entry bookkeeping once ledgers got fast enough to lie. The web got HTTPS once traffic was worth intercepting. Software supply chains got SBOMs once dependencies started shipping malware. AI agents are now writing the code that ships to production — and the only record of their intent is a paragraph the agent wrote about itself.

RoboTruth is the first product in **The Receipts Protocol** — a deterministic, cite-by-cite record of what an AI agent claimed versus what it actually did, issued by a system that itself contains no AI. Pull requests are simply the first surface where the gap is visible at file-and-line resolution. Paste a public GitHub PR; in seconds you get a **receipt** — verdict, grade, and every undisclosed change cited at `file:line`. *No model in the verdict path. The robot doesn't get to grade its own homework.*

## Why now

In May 2026, a large and fast-growing share of pull requests on active repositories are agent-authored. The reviewer's job has quietly inverted: from *writing code and rubber-stamping reviews* to *reading code they didn't write, written by something that can't be cross-examined*. The PR description — once a courtesy from a colleague — is now an unaudited claim by a non-human author with no reputational skin in the game. Every prior wave of automation produced a receipt layer once the speed of production outran the speed of trust. This is that moment for agentic code.

(Christian Haller's "Intent-Driven Verification" essay, published May 17 2026, names this exact gap from the other direction. RoboTruth is the first product built on the same premise.)

## How it works

The verdict path is deterministic by design. LLMs do not decide.

1. **Ingest** the PR title, body, and unified diff via GitHub's public API.
2. **Extract claims** with labeled-heuristic regex over the human-written lead of the PR body, surfaced back to the user as an *editable* claim list — so a bad parse is corrected before it's shared, and the "how do you know what it claimed?" objection is defused inside the UI itself.
3. **Scan** the diff with four deterministic passes — `dangerous_primitives`, `dependencies`, `scope_drift`, `security_guard`. Each flag carries file, line, severity, and the literal evidence.
4. **Grade** with a pure function whose decomposition is shown on the receipt: *"D: 1 undisclosed (1 critical), 0 unhonored; score=3."*

One engine — ~590 lines, no ML libraries — is imported by the web app, the MCP server, the per-repo scorecard, and the upcoming CLI. **No adapter contains audit logic.** The category lives in the function, not the surface.

The engine is **precision-biased**: it never accuses, it cites. Claims it can't verify from the diff surface as *unverified*, not as lies. The brand decision is that **false positives are the failure mode we refuse, false negatives are the failure mode we own and disclose** — an accountability product that ever wrongly accuses an honest PR is no longer one. Every flag carries the literal evidence the regex matched so a reader can audit the auditor.

## The receipt and its surfaces

The receipt itself is a screenshot-worthy card: verdict word, letter grade, three buckets (Delivered / Undisclosed / Unhonored), every flag cited at `file:line`, math decomposed on screen. Every share link renders the verdict card as its OpenGraph preview — when a receipt lands in Slack or X, the catch is already self-explanatory.

Beyond the single-PR receipt, the same engine fans out:

- **Wall of Shame** — a public feed that surfaces caught bot-authored PRs as audits run.
- **Per-repo scorecard** — `/repo/{owner}/{name}` audits the recent PRs of any public repo on demand and emits an honesty score.
- **MCP server** — a stdio server (install via `uv pip install -e .` from the repo) that exposes `audit_pr` to Claude Code, Cursor, and Cline. The agent audits the PR it just opened. Self-incrimination, in-workflow.
- **GitHub Action** — drops into any repo's CI; on every bot PR it posts the verdict *inline as a PR comment* — badge, letter grade, top flags at `file:line`, link to the full receipt — and edits its own comment on re-runs instead of spamming. The audit lands where reviewers already are, the CI gate stops carrying no context, and every commented PR is an organic impression.
- **Deploy Receipt preview** — [`/deploy/example`](https://robotruth-rdft.vercel.app/deploy/example) shows the same receipt grammar applied to a deployment-agent claim. Same verdict words, same three buckets, same evidence citations at `resource:line`. The scanners are different; the protocol is the same.

## Who it's for

The staff engineer who is now the bottleneck on agent-authored PRs. In 2026 a tech lead reviews more pull requests than they write, and the ones they don't write are the ones written by something they cannot cross-examine. The reviewer is the customer. The agent is the subject. The receipt is the artifact that closes the loop without expanding the reviewer's day.

A second-order audience falls out of the Wall and the Bot Leaderboard: the agent vendors themselves. Once a bot's honesty carries a public score, its makers have a reputation to defend — and a reason to make their agent disclose more. The reviewer is the customer; the leaderboard is what makes the vendors care.

## Tools used

- **Engine:** Python — `httpx`, `pydantic`, `unidiff`. No ML libraries.
- **Surfaces:** Next.js 16 frontend on Vercel · FastAPI on Vercel Python functions · Upstash Redis-backed durable receipts (file-backed fallback) · Python MCP SDK for the stdio server.
- **Verification:** 85 pytest tests — 72 engine (claim extraction, all four scanners, grading logic) plus 13 API-endpoint tests. TypeScript strict mode passes on the web surface. Every scanner has regression tests pinning the precision decisions made during the build.
- **Build copilot:** Claude Code (Opus 4.7). Every architectural call — engine-vs-API split, deterministic verdict path, claim-editor UI as precision insurance, MCP-as-distribution, Wall attribution policy (bots only / humans anonymized) — was worked through with the assistant in full transparency. This submission was itself adversarially edited by parallel agent reviewers before final draft.
- **Analytics:** The funnel hypothesis — *receipts spread (high share rate), evidence doesn't always follow them home (low submit rate)* — is the measurement we designed around. Eight named events (`landing_view → pr_pasted → receipt_generated → receipt_shared → submitted_to_wall`) fire to a working sink — our own `/api/events` route, which is the analytics that exists today. **Novus** (the hackathon's analytics sponsor) layers on top: the Pendo agent it runs on is embedded in the live site, and our funnel-event forwarding to it is wired behind a single env var (`NEXT_PUBLIC_NOVUS_SITE_ID`) that stays a no-op until it's set — so no Novus traffic has been recorded yet. What Novus *has* already delivered is validation: its own AI independently scanned RoboTruth, reconstructed its personas, product areas, and user flows accurately, and re-derived the engine's top precision risk unprompted — third-party confirmation from the sponsor's own tooling, not a claim of ours. The share→submit cliff is the next surface to design for — not more scanners.

## What I learned

**Determinism is the brand.** Shipping an LLM as the judge would have been faster — and would have killed the product. *"No model in the verdict path"* answers more judge questions in nine words than any diagram.

**Show your math, or you're just another opinion.** Every flag cites `file:line`. The grade decomposes on screen. The receipt footer names the methodology. An accountability product that can't itself be audited isn't one.

## What this is, finally

Agents are now writing software faster than humans can read it. That asymmetry will not reverse; it will compound. Either every agent action becomes auditable at the resolution it was performed at — or trust in agent-authored code collapses to the speed of human review, and the productivity story of this decade collapses with it.

RoboTruth is the first receipt. Pull requests are the first surface. The next surfaces — deployment agents, customer-comms agents, financial agents, ops agents, scheduler agents — are already shipping work, already narrating themselves, and already lying about it. The category is the gap between what the robot said and what the robot did.

**GitHub cannot audit GitHub. Anthropic cannot audit Claude.** The umpire has to be third-party and deterministic — that's a structural position, not a head-start. It is the only position where the answer to *"did the robot lie?"* cannot itself be a lie.

> *The robot doesn't get to write its own performance review.*

---

*Built greenfield May 20 – June 20, 2026, for Mind the Product's World Product Day 2026 hackathon.*
