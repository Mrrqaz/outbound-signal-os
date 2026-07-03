# ICP: Outbound Signal OS (fictional, demo-scoped)

This is a sanitized, fictional ICP built for this repo's worked examples. It is not Autoage's real ICP: see `context/icp.md` in the production repo for that (not included here).

## Who this system targets

B2B software companies showing an active, recent buying signal tied to sales/GTM capacity: not a static firmographic list, a **signal-triggered** list. The system re-scans continuously; a company only enters the pipeline because something changed recently, not because it matched a filter six months ago.

## Fit criteria

| Signal | Weight | What qualifies |
|---|---|---|
| Company size | High | 20–500 employees. Below 20, no real GTM budget yet. Above 500, sales cycle and buying committee size change the approach. |
| Industry | High | B2B SaaS / software / data infrastructure. Adjacent (fintech, martech, dev tools) counts partially. |
| Growth/hiring signal | High | Actively hiring for sales, GTM, or revenue-operations roles in the last 30 days: the core "why now." |
| Funding stage | Medium | Seed through Series C. Pre-seed rarely has budget; Series D+ usually has an established GTM motion already. |
| Geography | Medium | US/UK primary; other English-speaking markets secondary. |
| Existing tooling signal | Low | Runs a comparable or adjacent tool already (evidence of GTM sophistication, not necessarily a red flag). |

## Exclusions

- Agencies and consultancies selling GTM services themselves (channel conflict, not a buyer).
- Companies under 20 employees with no funding signal (no budget yet).
- Government, education, and regulated-industry buyers requiring a procurement process this system isn't built for.

## Why-now requirement

A lead only qualifies with a **recent, specific, evidence-backed signal**: a job posting, a funding announcement, a leadership change, a product launch: not a static match to the criteria above. Fit describes who's a good target; the signal is what makes today the day to reach out. See `directives/signal_sourcing.md` and `directives/icp_filtering.md`.
