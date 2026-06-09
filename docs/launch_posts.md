# Launch posts — multi-platform burst (post AFTER product is "done" + video is up)

> Honest-traffic engine. The goal is real humans walking the funnel (paste → receipt → share),
> which is what populates the Novus dashboard legitimately and feeds the submission's "Shippedness"
> story. **No fabricated usage numbers in any post** — this product is literally about not lying.
> LinkedIn copy lives in `linkedin_posts.md`. These are the other surfaces.
>
> Sequence: post the **video** first (YouTube/Vimeo/Youku — these are the ONLY hosts Devpost accepts; NOT Loom), then point every post at it + the live site.
> Asset for image posts: a real receipt card (a SNEAKY catch reads best; HONEST·A is the clean fallback).

---

## 1 · Show HN

**Title:**
> Show HN: RoboTruth – deterministic receipts for whether an AI bot lied in its PR

**Comment (post immediately as the first comment):**
> A fast-growing share of PRs on active repos are now agent-authored (Copilot, Cursor, Dependabot, Claude, etc.). The PR description is the agent's own narration — there's no auditor and no receipt, just an unsigned claim by a non-human author.
>
> RoboTruth takes a public GitHub PR URL and returns a deterministic receipt: what the agent *claimed* in its description vs. what the diff *actually* did, with every divergence cited at `file:line`. One verdict (HONEST / MOSTLY HONEST / SNEAKY / LIAR), one letter grade, and the grade's math shown on the card.
>
> The design decision I care most about: **there is no LLM in the verdict path.** Claims are pulled from the PR body with transparent heuristics (and you can edit what it read before sharing); the diff is read by four deterministic scanners; a pure function emits the verdict. An accountability tool that can't itself be audited isn't one — so every flag carries the literal evidence it matched.
>
> It's precision-biased on purpose: it never accuses, it cites. Claims it can't verify from the diff show up as *unverified*, not as lies — false positives are the failure mode I refuse.
>
> There's also a GitHub Action that posts the verdict inline on the PR, an MCP server so an agent can audit the PR it just opened, and per-repo honesty scorecards.
>
> Live: https://robotruth-rdft.vercel.app — paste a real PR and you'll get a real receipt. Engine is ~590 lines of Python, no ML libraries. Happy to go deep on the scanner heuristics or the false-positive tradeoffs in the comments.

---

## 2 · Reddit (r/ExperiencedDevs or r/programming)

**Title:**
> I built a tool that audits whether AI-written PRs actually did what they claimed — deterministically, no LLM in the verdict

**Body:**
> Reviewing agent-authored PRs has quietly become the job. The problem: the PR description is written by the same agent that wrote the code, and the only way to know if it's honest is to read every line of the diff yourself.
>
> So I built RoboTruth. Paste a public GitHub PR and it returns a "receipt": claimed vs. actually-did, every undisclosed change cited at `file:line`, a verdict word, and a grade with its math shown.
>
> The part I'd want feedback on from this sub: I deliberately kept **all AI out of the verdict path**. Claims are extracted with editable heuristics; four deterministic scanners read the diff; a pure function grades it. It's biased toward precision — if it can't prove a claim false from the diff, it marks it *unverified* rather than calling the bot a liar. I'd rather miss a catch than wrongly accuse an honest PR.
>
> There's a GitHub Action (posts the verdict as a PR comment), an MCP server, and per-repo scorecards too.
>
> Live, no signup: https://robotruth-rdft.vercel.app — try it on a Dependabot or Copilot PR. Would genuinely like to hear where the heuristics break.

---

## 3 · X / Twitter thread

**1/**
> More and more pull requests are written by AI agents.
> The PR description? Also written by the agent.
> So who checks if the robot told the truth about what it did?
>
> I built RoboTruth. Paste an AI-written PR → get a receipt. 🧵

**2/**
> A receipt = what the agent *claimed* vs what the diff *actually* did.
> Every undisclosed change cited at `file:line`.
> One verdict: HONEST / SNEAKY / LIAR. One grade. Math shown.

**3/**
> The key decision: there is **no AI in the verdict path.**
> Heuristics read the claims, deterministic scanners read the diff, a pure function grades it.
> An auditor you can't audit isn't one. The robot doesn't get to grade its own homework.

**4/**
> It's precision-biased: it never accuses, it cites.
> Can't prove a claim false from the diff? It says *unverified* — not "liar."
> False positives are the one failure mode I refuse.

**5/**
> Also ships as a GitHub Action (verdict posted right on the PR) and an MCP server (the agent audits the PR it just opened — self-incrimination, in-workflow).

**6/**
> Live, no signup. Paste a real PR:
> robotruth-rdft.vercel.app
>
> Built for @MindThePRoduct World Product Day 2026. #EveryoneShipsNow
> Did the robot lie? Find out before you merge.

---

## 4 · Instagram (caption for the receipt-card image or a 30s clip)

> More and more code is written by AI now. The AI also writes the summary of what it did. 🤖
>
> RoboTruth checks if the robot told the truth — paste any GitHub pull request and get a receipt: what it *claimed* vs what it *actually* changed, line by line. No AI in the verdict. It can't fake its own receipt.
>
> Did the robot lie? Link in bio → robotruth-rdft.vercel.app
>
> @mindtheproduct #EveryoneShipsNow #WorldProductDay #AI #coding #devtools #buildinpublic

---

## 5 · README Honesty Badge

Drop the live badge at the top of the `robotruth` README (and any other public repo — every repo visitor becomes a click):

```markdown
[![RoboTruth](https://robotruth.vercel.app/api/badge/Alexander-Sorrell-IT/robotruth.svg)](https://robotruth-rdft.vercel.app/repo/Alexander-Sorrell-IT/robotruth)
```

Generic snippet for anyone else (also shown on `/badge`):

```markdown
[![RoboTruth](https://robotruth.vercel.app/api/badge/OWNER/REPO.svg)](https://robotruth-rdft.vercel.app/repo/OWNER/REPO)
```
