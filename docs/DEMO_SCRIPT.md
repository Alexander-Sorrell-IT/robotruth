# RoboTruth — Demo Video Script

**Target length:** 2:30. Hard cap 3:00.
**Format:** Screen recording + voice-over. No talking-head. 1080p, 30fps.
**One-line pitch you must land in the first 8 seconds:** *"Paste an AI-written PR — see what it actually did."*

> **Production notes**
> - Two cuts: **MCP-in** (this script) and **MCP-out** (skip §6). Pick by judge-legibility test before submitting. For the MCP-out cut, run **§5.5 (PR comment bot)** as the in-workflow flex instead — it's more legible to non-engineer judges than MCP.
> - Tabs pre-opened: receipt example, Wall of Shame, per-repo scorecard, Novus dashboard, terminal with MCP demo, **and a real PR with the RoboTruth comment on it** (e.g. the repo's own PR #6 — RoboTruth auditing itself).
> - Cursor zoom on during URL paste and verdict reveal. Off otherwise.
> - Music: 80 BPM lo-fi, ducked under VO. Hard cut on stinger at 0:35 verdict reveal.
> - Lower-third: `robotruth-rdft.vercel.app` persistent in bottom-right after 0:30.

---

## SHOT LIST

### 0:00 – 0:08 · COLD OPEN — the question

**Visual:** Full-screen GitHub PR page. Title visible: *"Refactor auth middleware — only touches login flow, no breaking changes, added tests."* PR author badge: `dependabot[bot]` or similar. Slow zoom on the PR description.

**VO:**
> "In 2026, more and more pull requests are written by agents. They tell you what they did — in their own words."

**Sound:** Soft typewriter clack under VO.

---

### 0:08 – 0:18 · THE PROBLEM

**Visual:** Cursor scrolls the PR diff — 600 lines blur past. Cut to a tired reviewer-cursor sitting on the "Merge" button. Cursor hovers. Doesn't click.

**VO:**
> "But the description is the agent's own narration. Did it only do what it said — or did it quietly do more? You don't know unless you read every line. Nobody reads every line."

---

### 0:18 – 0:30 · THE PASTE

**Visual:** Cut to RoboTruth landing — `robotruth-rdft.vercel.app`. Hero text *"Did the robot lie?"* fills the frame. Cursor pastes a real PR URL. Clicks **Audit**. Loading state (~1s).

**VO:**
> "RoboTruth reads the diff for you. Paste any public GitHub PR. Get the receipt."

---

### 0:30 – 0:55 · THE CATCH (the money shot)

**Visual:** Receipt card snaps in. Big verdict word — **SNEAKY** — and grade **D** in the hero. Three columns: ✅ Delivered, ⚠️ Undisclosed, ❌ Unhonored. Camera tracks down to one undisclosed flag — highlighted — `auth/middleware.ts:42` with the literal removed-line evidence.

**VO:**
> "Here's what the PR claimed. Here's what it actually did. *This* line was removed — a security check the description never mentioned. Cited at file and line. Deterministic. No AI guessed this."

**Sound:** Single hard stinger on the verdict word reveal.

---

### 0:55 – 1:10 · THE PROOF — show the math

**Visual:** Cursor opens the small **"Show math"** disclosure under the grade: *"D: 1 undisclosed (1 critical), 0 unhonored; score=3."* Then hovers the footer: *"Deterministic. Every flag cites file:line. No AI opinions."*

**VO:**
> "The verdict is a pure function over deterministic scanners. The grade shows its work. Claim parsing uses transparent heuristics — and you can edit what we read, before you share."

**Visual cue:** quick 2s flash of the claim editor — user toggles off a misread claim, re-audits, grade updates.

---

### 1:10 – 1:25 · THE SPREAD

**Visual:** Click **Copy share link**. Cut to iMessage / Slack preview where the link unfurls — the OG image *is* the verdict card. Then a quick three-up of the link previewing identically on Slack, X, and LinkedIn.

**VO:**
> "Every receipt has its own link. The preview *is* the catch — so when this shows up in your team chat, the conversation is already over."

---

### 1:25 – 1:45 · THE FRONT DOOR — Wall of Shame

**Visual:** Navigate to `/wall`. **Seed the Wall with genuine catches before recording** — run RoboTruth on a few known-sneaky public bot PRs so the feed is real, not staged (the Wall auto-populates from any SNEAKY/LIAR audit). Cursor hovers two caught PRs — each verdict animates in. Click one → its receipt fills the frame for a beat. *If it's still empty at record time, do not fake a grid* — show the honest "Live · scanning · the bots are behaving" empty state and demonstrate a fresh catch via a paste instead.

**VO:**
> "Browse the Wall of Shame — every receipt here is a real catch on a public bot. New ones land as audits run."

---

### 1:45 – 2:00 · THE DEPTH — per-repo

**Visual:** Type `owner/repo` into the per-repo input. Page renders an honesty score (e.g., *"71% honest"*) over the repo's last eight PRs as small receipt tiles, each with a verdict.

**VO:**
> "Or audit a whole repo. Honesty score, every recent PR scored. Same engine, fanned out."

---

### 1:45 alt · §5.5 · THE LOOP — PR comment bot (use as the flex in the MCP-out cut)

**Visual:** A real GitHub PR page. The CI checks list shows **RoboTruth Audit**. Scroll down to the bot's comment — the RoboTruth receipt rendered *inline on the PR itself*: **✅ HONEST · Grade A** (or a SNEAKY catch on a juicier PR), top flags at `file:line`, **"View the full receipt →"** link. Cursor clicks the link → the full receipt card fills the frame.

**VO:**
> "Add the GitHub Action and RoboTruth audits every bot PR automatically — and posts the verdict right on the pull request, where reviewers already are. No new tab. The receipt comes to them."

**Note:** film this on a PR with a *non-trivial* catch if you have one; the repo's own PR #6 (HONEST · A) works as a clean fallback that proves it dogfoods.

---

### 2:00 – 2:20 · THE FLEX — MCP (cut this section for the MCP-out video)

**Visual:** Terminal. Claude Code session running. The agent opens a PR. Cursor invokes the `audit_pr` MCP tool. Receipt comes back inline. Verdict: **LIAR · F**. Agent's own output in the next line: *"Re-opening with the test file I missed."*

**VO:**
> "And because the engine is just a Python package, it's also a one-line MCP server. Drop it into Claude Code or Cursor — and the agent audits the PR it just opened. Self-incrimination, in-workflow."

---

### 2:20 – 2:30 · BRAND CLOSE

**Visual:** Cut to clean landing — `robotruth-rdft.vercel.app`. Tagline **"Did the robot lie?"** fades up. URL holds for 3 seconds. Cut.

**VO:**
> "RoboTruth. Did the robot lie? Find out before you merge."

---

## EDIT NOTES

- **Pick the PR carefully.** The 0:30 catch needs to be a visually compelling flag — a removed security check or a hidden dep bump reads better than a scope-drift flag. Pre-cache two candidates so you can swap if one renders weak.
- **Stinger discipline.** One stinger only, at 0:30 verdict reveal. A second stinger on the MCP catch (2:14ish) is okay, no more. Music does the rest.
- **Captions.** Auto-caption the VO, then proofread — judges sometimes scan muted.
- **End frame, not end card.** Last frame is the live URL, *not* a "Thanks for watching" card. They land directly.
- **B-roll budget.** Do not spend time on transition effects. Hard cuts only. This product's brand is precision; the edit should match.

## SHOT-CHECK BEFORE EXPORT

- [ ] Hero URL visible in lower-third by 0:30 and held to end
- [ ] Verdict word reveal is the loudest visual beat in the whole video
- [ ] At least one shot of a flag at `file:line` (the credibility moment)
- [ ] Math/footer shown for at least 2s (defuses the "is this AI?" judge question)
- [ ] OG preview shown in at least one real chat surface (Slack or iMessage)
- [ ] Wall of Shame and per-repo each on screen for ≥10s
- [ ] No console / dev-tools artifacts in any frame
- [ ] Final frame is the bare live URL
