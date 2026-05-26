# LinkedIn build-in-public series — RoboTruth

> Strategy per distribution agent + per-judge agent:
> Valeria Khokhlova (Head of Community, MtP) is the **marginal voter**.
> Her objection — *"is this travelling in the community?"* — is the only
> one ink can't close. Live signal in the world over time is the fix.
> Post #1 should land **tonight (2026-05-26 or first thing 2026-05-27)**
> so the hashtag is warm by the time other judges browse activity.

---

## Post #1 — Origin / "10 days ago this category got a name"

**Channel:** LinkedIn (primary) + X (secondary, ~70% of LinkedIn text)
**Best post window:** Tuesday 2026-05-27, 8-10am or 12-1pm CT
**Tags:** `@MindTheProduct` `#EveryoneShipsNow` `#WorldProductDay`
**Asset:** One screenshot — a real receipt card (verdict + grade + file:line evidence). Receipt ID `sNa-g3VK` (facebook/react#36533 HONEST · A) works as a clean asset, OR a SNEAKY catch once we have one.

---

### Draft (LinkedIn — long form)

10 days ago, Christian Haller published an essay called "Intent-Driven Verification."

The thesis, paraphrased: in 2026 most software is being written by AI agents, and the PR description — the only record of what the agent claims to have done — is **the agent's own narration**. There is no auditor. There is no receipt. There is only an unsigned claim by a non-human author with no skin in the game.

He named the gap.

I built the first product that fills it.

It's called **RoboTruth**. You paste a public GitHub PR URL. You get back a deterministic receipt — what the AI *claimed* in its description, what the diff *actually* shows it did, and every divergence cited at `file:line`. Three buckets: delivered, undisclosed, unhonored. One verdict word (HONEST · MOSTLY HONEST · SNEAKY · LIAR). One letter grade. The math is shown on the receipt.

**No model in the verdict path.** The auditor itself can't fake the receipt — because the auditor has no AI in it. Heuristics extract claims; deterministic scanners read the diff; a pure-function grader emits the verdict. An accountability product that can't itself be audited isn't one.

Built it for `#EveryoneShipsNow`, Mind the Product's World Product Day 2026.

Live now: **robotruth-rdft.vercel.app** — paste a real PR, get a real receipt.

Pull requests are the first surface where the claim-vs-action gap shows up at file-and-line resolution. They won't be the last. Deployment agents narrate themselves. So do customer-comms agents. So do financial agents. Every era of automation gets a receipt layer once production outruns trust. That moment for agentic code is now.

The category is **The Receipts Protocol**. RoboTruth is the first instance.

The robot doesn't get to write its own performance review.

---
`#EveryoneShipsNow` `#WorldProductDay` `@MindTheProduct`

---

### Draft (X — short, thread-friendly)

10 days ago Christian Haller named the gap: AI-written PRs are narrated by the AI itself, and nobody audits the narration.

I built the first product that does.

**RoboTruth** → paste any public GitHub PR → deterministic receipt of what the AI claimed vs what it actually did.

No model in the verdict path. The auditor itself can't fake the receipt — because the auditor has no AI in it.

Live: robotruth-rdft.vercel.app

Built for `#EveryoneShipsNow` `@MindThePRoduct`'s World Product Day 2026.

The robot doesn't get to write its own performance review.

---

## Notes for the post

- **Don't link Haller's post directly** unless you've messaged him first (recommended). Naming + paraphrasing is fine.
- **The screenshot matters more than the text.** A clean receipt card (verdict word in color, file:line citations visible, "no model in the verdict path" footer) is what stops the scroll. Use the actual receipt page screenshot, not a marketing graphic.
- **Reply to your own post in the comments** within 30 min with a *second* image — the Wall of Shame page OR the per-repo scorecard for a famous repo (`/repo/facebook/react`). LinkedIn promotes posts with author comment activity in the first hour.
- **Don't @-tag Joe Dreimann or Dave Killeen** in this post even though they're judges. Tag pattern matters; @-tagging judges on submission content reads as gaming. Engage on *their* posts substantively over the next 24 days instead.

## Posts #2-#7 — planned cadence

| # | Date | Hook | Asset |
|---|---|---|---|
| 2 | 2026-05-31 | "I audited 50 bot-authored PRs across X repos. The grade distribution surprised me." | Bar chart receipt grades + 3 sample receipts |
| 3 | 2026-06-04 | "AI Accountability is a category, not a feature." (reframe / depth post) | Diagram: 4 next surfaces of the Receipts Protocol |
| 4 | 2026-06-08 | "Graded a PR from [public maintainer] — they passed. Receipt:" | One A-grade real receipt, tag the maintainer (A/B only — never publicly tag F-grade) |
| 5 | 2026-06-11 | "What 200 audited PRs taught me about AI honesty." (the viral artifact — see /honesty-index when shipped) | Mini-report PDF or `/honesty-index` link |
| 6 | 2026-06-15 | "MCP server is open. Your Claude can now audit PRs natively." | 20-sec gif of Claude Desktop running the MCP tool |
| 7 | 2026-06-19 | "Submission day: 25 days, 1 builder, X receipts shared. Thanks @judges." | Composite stats card with handles |

Each post needs a *new artifact* (number, screenshot, feature) — not a restated pitch. Valeria notices low-effort hashtag-stuffing.
