# ICP Filtering

**Status:** Policy (Layer 1). Read by `.claude/skills/icp-qualify/SKILL.md`.
**Owner:** Outbound Signal OS.

## Purpose

Filter the sourced batch (from `signal_sourcing.md`) down to leads worth spending research and outreach effort on, before any paid step runs. This is the gate that protects `cost_control.md`'s spend budget: nothing expensive happens to a lead that hasn't cleared this gate.

## Scoring model

Score every lead on three weighted categories against `context/icp.md`:

- **ICP fit**: company size, industry, tech-stack alignment.
- **Signal strength**: recency, specificity, and count/diversity of signals found.
- **Engagement potential**: public activity level (LinkedIn presence, content engagement) as a proxy for reachability.

See `.claude/skills/icp-qualify/SKILL.md` for the exact point weights and tiers, and `executions/icp_score.py` for the reference scoring function.

## The missing-data rule

If a scoring category is missing data (no signal-strength evidence found, no engagement data available), that category is capped, not scored as zero and not skipped. A lead that scores well on the categories with data but is missing a whole category should not look identical to a lead that was fully evaluated and scored well everywhere. The cap makes "partially evaluated" visibly different from "fully evaluated and good."

## The upstream-qualification exemption

A lead that already carries a real qualification decision from an upstream process it was imported through (a pre-vetted list, a prior screening pass with its own documented criteria) does not need to be re-run through this gate. Re-scoring it against this system's signal-based criteria would be redundant at best (the work was already done) and miscalibrated at worst (the two scoring systems don't measure the same thing). This exemption applies only when the upstream decision is explicit and traceable: never assume a lead was pre-vetted without evidence.

This directive exists because an earlier version of this gate re-checked every lead uniformly and it produced exactly this false-redundancy problem. See `context/decisions-log.md`, 2026-06-20.

## Tiers and what happens next

Leads score into tiers (see the skill for exact thresholds). Top-tier leads proceed to `research.md`. Bottom-tier leads are held, not deleted: a held lead can re-qualify later if a new, stronger signal appears.
