# Signal Sourcing

**Status:** Policy (Layer 1). Read by `.claude/skills/signal-harvest/SKILL.md`.
**Owner:** Outbound Signal OS.

## What counts as a signal

A signal is evidence that something changed recently at a company, in a way that creates a plausible reason to reach out now. Not a static firmographic match: a firmographic match tells you *who*, a signal tells you *why now*. See `context/icp.md` for the fit criteria a signal gets checked against downstream.

## Signal taxonomy (priority order)

1. **HIRING**: a public job posting for a sales, GTM, or revenue-operations role. The single strongest, most repeatable signal source: it's public, dated, and implies budget.
2. **FUNDING**: a funding announcement (seed through Series C is in-ICP; see `context/icp.md`).
3. **TECHNOLOGY**: a detectable change in tech stack (a new tool added, a competitor's tool removed).
4. **GROWTH**: headcount growth, new office/market expansion, a product launch.
5. **PAIN**: a public complaint, review, or support-forum post indicating an unmet need (weakest signal, highest false-positive rate; requires corroboration before use).

## Source priority

Prefer public, structured sources over unstructured ones: job boards and company career pages first, then funding databases, then general news/press, then social platforms. A signal from a structured source (a job listing with a posted date) is more trustworthy than an inferred one (a LinkedIn post implying growth).

## Rate and freshness

- A HIRING or FUNDING signal is only actionable within 30 days of its posted/announced date. Past that window, re-verify it's still live before using it as the "why now."
- Collect signals into a batch (a sheet/workbench row per company), not one-off. The batch is what feeds `icp-qualify` next.

## What this directive does not cover

Whether a sourced signal actually qualifies the company (that's `icp_filtering.md`), and how much a signal is allowed to cost to source (that's `cost_control.md`).
