# Cost Control

**Status:** Policy (Layer 1). Read by `.claude/skills/spend-and-cost-guard/SKILL.md`.
**Owner:** Outbound Signal OS.

## Purpose

Every stage past `icp-qualify` costs real money: deep research calls, paid enrichment, LLM generation at scale. This directive is what keeps that spend proportional to lead quality instead of uniform across every lead regardless of fit.

## The spend gate

Before any paid step runs on a lead, a cheap, deterministic pre-check runs first: does this lead clear the ICP gate (`icp_filtering.md`)? If not, the paid step does not run, full stop: no "run it anyway to be safe." The pre-check is intentionally much cheaper than the step it's gating; the entire point is spending pennies to avoid spending dollars on a lead that was never going to qualify.

## Rate-limit and key management

Where a paid provider enforces a rate limit or a credit ceiling, the system rotates across multiple provisioned keys rather than stalling the pipeline on one exhausted key. Rotation is a fallback for capacity, not a way to bypass a provider's terms: if all keys are exhausted, the pipeline waits or flags for a human decision, it does not find a workaround.

## Caching

A lead that was already researched or enriched within a defined freshness window is not re-processed at full cost. Cache the result and reuse it; only re-run the paid step if the cached result has aged past the freshness window or the lead's signal set has materially changed since.

## Per-lead spend visibility

Track cumulative spend per lead across every paid step it passes through. This is what makes it possible to answer "is this system spending proportionally to lead quality" rather than just "is this system within budget this month": a system can be within budget and still be spending evenly across bad and good leads, which defeats the point of the ICP gate upstream.

## What this directive does not cover

The ICP scoring formula itself (`icp_filtering.md`): this directive only covers what happens once that score exists.
