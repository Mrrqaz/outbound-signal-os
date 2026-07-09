---
name: icp-qualify
description: Score every lead in the sourced batch on three weighted categories, ICP fit (0–40), signal strength (0–35), and engagement potential (0–25), against a 100-point formula, then tier it TIER_1 through TIER_4 and route TIER_1/TIER_2 leads to research while holding TIER_3/TIER_4 for later re-qualification. Applies a 50%-of-max cap, never zero, never skipped, to any category with no real evidence, and exempts leads that already carry an explicit upstream qualification decision. Run after signal-harvest hands off a new batch, or when asked to "score this lead," "qualify this batch," "why did this lead get held," or "check the ICP fit."
user_invocable: true
---

# ICP Qualify

Stage 2 of the pipeline: bad fit gets filtered. Takes the batch `signal-harvest` sourced and scores every lead in it before any paid research or outreach spend touches it. A lead scored wrong here either burns research budget chasing a company that was never going to buy, or leaves a genuinely hot, well-fitting signal sitting unscored in the pile until its window closes. Every lead runs through the same three-category formula, the same way, so a strong TIER_1 lead never gets buried behind a mediocre one just because it was scored by whoever glanced at the batch first.

Adapted from janskuba's `outbound-agents` repo (github.com/janskuba/outbound-agents, 74 stars / 25 forks), the `.claude/agents/lead-prioritizer.md` agent. The 100-point three-category formula, the exact point sub-splits inside each category, and the four-tier action-mapped system (TIER_1 through TIER_4) are that agent's design, verified directly against its source file. A secondary reference, openfunnel's `openfunnel-skills` repo, the `score-and-tier` skill, describes a similar 0–100 evidence-backed score assigned to new accounts as they enter on daily signals (its docs are explicit that already-tiered accounts stay put rather than re-tiering, the opposite of this skill's held-lead re-qualification), and I could not confirm an exact weight breakdown, so no number in this skill is sourced from it. It's noted here only as a second real-world precedent for the pattern, at a lower confidence than the primary source.

## Operating Rules (read first)

- **Score fit, signal strength, and engagement as three separate categories, then sum them.** Don't eyeball one blended "looks good" number. Fit answers who they are, signal answers why now, engagement answers whether they're actually reachable, and collapsing that early hides which one is doing the work.
- **The missing-data cap is mandatory on any category with no real evidence behind it, not optional.** Never score it a true zero (indistinguishable from "evaluated and bad") and never skip it (that breaks the total). Cap it at 50% of that category's max instead.
- **Check the upstream-qualification exemption before scoring anything, not after.** A lead carrying an explicit, traceable qualification decision from an upstream process skips this gate entirely. Re-scoring it against a different system's criteria is redundant at best and miscalibrated at worst.
- **This gate exists to protect spend downstream.** Nothing expensive, deep research, enrichment, gets spent on a lead that hasn't cleared this gate or been explicitly exempted (see `directives/cost_control.md`).
- **Only score what's actually evidence-backed.** A missing field with no partial evidence at all is a missing category (Step 5), not a number invented to force a clean tier.
- **TIER_3 and TIER_4 are a hold, not a delete.** A held lead re-qualifies the moment `signal-harvest` surfaces a new, stronger signal for that company.

## Intended Integrations (not live in this demo)

- **An enrichment waterfall** would populate and verify the fit fields, employee count, industry classification, detected tech stack, instead of relying on whatever `signal-harvest` already captured at ingestion. In production that waterfall is **Prospeo** for email discovery, **Apollo** for contact and company data, and **Floqer** for the enrichment orchestration and fallback across providers, cheapest reliable source first, escalating only when a field comes back empty.
- **A LinkedIn or social-data API** would feed the engagement fields directly, posting frequency, recent activity, engagement counts, instead of this skill scoring off whatever public detail already happens to be in the batch.
- **`system-of-record-sync`** owns the actual write-back. The tier decision and category breakdown this skill produces don't get written to the lead record directly, that's the single-writer pattern this repo's `CLAUDE.md` describes. This skill hands off a scored, tiered lead; the write, with its one-line reason, happens downstream.
- None of these are wired into this repo. This is a demonstration of the scoring and gating logic against the fixture batch in `context/example-leads.md`, not a live pipeline.

## Step 1: Pull the Sourced Batch

Take the batch as handed off from `signal-harvest`, one row per company, each carrying whatever signal(s) `directives/signal_sourcing.md` found and whatever firmographic detail was captured at ingestion (see `context/example-leads.md` for the batch shape this repo uses). Note what's present per lead: fit-relevant fields (industry, size, tech signal), the signal itself (type, date, source), and any engagement-relevant public detail already on file. Missing fields aren't guessed here. They carry forward into the missing-data rule in Step 5.

## Step 2: Check the Upstream-Qualification Exemption First

Before spending any scoring effort, check whether the lead already carries an explicit, traceable qualification decision from an upstream process (a pre-vetted list with its own documented screening criteria, a prior real qualification pass, not just something that looks pre-vetted). If yes: skip Steps 3 through 6 entirely and pass the lead straight to Step 7 carrying its upstream decision as-is. Re-running it through this system's signal-based criteria would be redundant at best (the work is already done) or miscalibrated at worst (the two scoring systems don't measure the same thing). See `directives/icp_filtering.md` and the 2026-06-20 entry in `context/decisions-log.md`, where an earlier version of this gate re-checked every lead uniformly and produced exactly this problem. This exemption never fires on a guess. No explicit, traceable upstream decision on record means the lead gets scored.

## Step 3: Score ICP Fit (0–40)

| Category | Points | What it scores |
|---|---|---|
| Industry relevance | 0–15 | Direct B2B SaaS / software / data-infra match scores up to 15; adjacent (fintech, martech, dev tools) gets partial credit; unrelated scores 0. Maps to the Industry row in `context/icp.md`. |
| Company size fit | 0–15 | Squarely inside the 20–500 employee band scores up to 15; near an edge of the band scores partial credit; outside the band scores 0. Maps to the Company size row. |
| Tech-stack alignment | 0–10 | Evidence of running a comparable or adjacent tool scores up to 10; no tech-stack signal found scores 0. Maps to the Existing tooling signal row. |

**Fit score = sum, 0–40.**

## Step 4: Score Signal Strength (0–35)

| Category | Points | What it scores |
|---|---|---|
| Recency and specificity | 0–15 | A dated, specific signal inside `signal_sourcing.md`'s 30-day actionable window scores highest; a vague or aging signal scores lower. |
| Count and diversity | 0–10 | More than one corroborating signal (a hiring post plus a funding announcement, for example) scores higher than a single signal alone. |
| Signal rating | 0–10 | The HIGH/MED/LOW rating `signal-harvest` already assigned, following the taxonomy's priority order (HIRING and FUNDING rate highest; PAIN rates lowest and needs corroboration before it counts at all). |

**Signal score = sum, 0–35.**

## Step 5: Score Engagement Potential (0–25), Then Apply the Missing-Data Cap

| Category | Points | What it scores |
|---|---|---|
| LinkedIn activity | 0–10 | Posting frequency and recency on the contact's or company's LinkedIn presence. |
| Content engagement | 0–8 | Visible engagement (comments, shares, reactions) on that activity. |
| Approachability | 0–7 | A real, reachable public contact path: an open profile, a known email pattern, a prior touchpoint. |

**Engagement score = sum, 0–25.**

Then, for any of the three categories: if it carries a genuine evidence gap, either no real evidence at all (nobody could find LinkedIn activity, no engagement data available, no tech-stack signal either way) or a sub-score that truly could not be verified either way, that category is flagged missing and capped at 50% of its max. A category with no evidence at all scores the cap itself, never a true zero and never skipped outright.

| Category | Max | Cap when missing |
|---|---|---|
| Fit | 40 | 20 |
| Signal | 35 | 17 |
| Engagement | 25 | 12 |

The cap is a ceiling, not a floor. It applies after summing whatever partial evidence the sub-scores above actually found. An honest low partial read stays low. A partial read that would otherwise rival or beat a fully-verified score gets pulled back down to the cap, so a category nobody could actually verify never outscores one that was. This is `directives/icp_filtering.md`'s missing-data rule, implemented in `executions/icp_score.py`.

Flag `partial_evaluation: true` on the lead if any category was capped. That flag travels with the score into Step 7 and downstream, so whoever picks up the lead next can see it was a partial read, not a clean pass.

## Step 6: Total and Tier

**Total = fit + signal + engagement, 0–100.**

| Tier | Score | Action |
|---|---|---|
| TIER_1 | 80–100 | Work today |
| TIER_2 | 60–79 | Work this week |
| TIER_3 | 40–59 | Nurture |
| TIER_4 | 0–39 | Deprioritize |

## Step 7: Route the Tiered Lead

TIER_1 and TIER_2 leads (and any exempted lead carrying an upstream decision) hand off to `signal-research-dossier`, carrying the total score, the category breakdown, and the `partial_evaluation` flag. TIER_3 and TIER_4 leads are held, not deleted. A held lead comes back through this gate and can re-qualify the moment `signal-harvest` surfaces a new, stronger signal for that company (`directives/icp_filtering.md`).

## Worked Example (fictional)

Two leads from the batch in `context/example-leads.md`.

**Nova Systems Lab** (Maya Patel, Head of Sales, signal: hiring SDRs).

Step 2: No upstream qualification decision on record, this lead came in through `signal-harvest`'s normal path. Scored.

Step 3, Fit: industry relevance 15 (direct B2B SaaS match), company size fit 12 (well inside the band, not dead-center), tech-stack alignment 8 (an adjacent tool detected). **Fit = 35.**

Step 4, Signal: recency/specificity 15 (the SDR posting is dated inside the last week), count/diversity 8 (a second, corroborating GTM-adjacent posting found alongside it), signal rating 10 (HIRING is the taxonomy's top-priority signal type). **Signal = 33.**

Step 5, Engagement: LinkedIn activity 8 (Maya posts regularly), content engagement 6 (her posts draw real comments), approachability 6 (open profile, a known company email pattern). No category missing, nothing capped. **Engagement = 20.**

Step 6: Total = 35 + 33 + 20 = **88, TIER_1, work today.** This matches the 88% fit score already sitting on Nova's row in `context/example-leads.md`. The category breakdown above is what that number is actually made of.

Step 7: Hands off to `signal-research-dossier` with the full breakdown attached.

**QueryForge Cloud** (Owen Clarke, VP Growth, signal: hiring account executives, intake fit score 72%).

Step 2: No upstream qualification decision on record. Scored.

Step 3, Fit: industry relevance 13 (B2B software, not a dead-center SaaS/data-infra match), company size fit 13 (comfortably inside the band), tech-stack alignment 6 (an adjacent tool detected, a weaker signal than Nova's). **Fit = 32.**

Step 4, Signal: recency/specificity 13 (dated AE posting, inside the window), count/diversity 5 (only the one job posting found, no second corroborating signal), signal rating 8 (HIRING, but a slightly softer confidence read than Nova's). **Signal = 26.**

Step 5, Engagement: real evidence exists for two of the three sub-scores. QueryForge's LinkedIn page posts several times a week (LinkedIn activity 10), and a few of those posts carry visible comment threads (content engagement 5). Approachability has no evidence at all, no open contact path or prior touchpoint was found. Raw engagement sums to 15. Because the category has a genuine coverage gap (approachability truly unverified, not just low), it's flagged missing and capped at 12 (50% of 25). **Engagement = 12, capped from a raw 15. `partial_evaluation: true`.**

Step 6: Total = 32 + 26 + 12 = **70, TIER_2, work this week.** Close to the 72% fit estimate already on the batch row, and lands in the same territory even after the engagement cap pulled a genuine 15-point read down to 12. Uncapped this lead would have scored 73, still TIER_2 here, but the cap is what keeps a partially-verified read from ever quietly outscoring a fully-verified one at a tier boundary.

Step 7: TIER_2, hands off to `signal-research-dossier` carrying the `partial_evaluation` flag so the next stage knows approachability still needs a real check.

## Rules

- Score fit, signal strength, and engagement as three independent categories before summing. Never blend them early or let a strong read on one category stand in for a weak one on another.
- The missing-data cap applies to any category with a genuine evidence gap. Never score that category a true zero, never skip it, and never let a partial read quietly outscore a fully-verified one past the cap.
- Check the upstream-qualification exemption before scoring anything. It applies only to an explicit, traceable upstream decision, never a guess that a lead "looks" pre-vetted.
- Held leads (TIER_3, TIER_4) stay held, not deleted. They come back through the gate on a new signal, not on a schedule.
- Every score carries its full category breakdown and its `partial_evaluation` flag downstream, not just the tier label, so whoever picks up the lead next can see why it landed where it did.
- If a required field is missing outright with no partial evidence at all, say so and score what's available. Never invent a firmographic or engagement value to force a clean tier.
- This gate protects spend. Nothing expensive happens to a lead before it clears this step or is explicitly exempted.
