# Outbound Signal OS: Agent Instructions

This is a reference/example implementation of an outbound lead-generation system, assembled to complement the Outbound system demo on my portfolio. **It is not the live production Autoage source**: no real credentials, client data, pricing, or proprietary scoring internals are in this repo. See `README.md` for the full disclaimer and sourcing notes.

The point of this repo isn't "here's a prompt that writes cold emails." It's: given a business problem (turn public buying signals into a qualified, researched, approved outbound pipeline), can I architect a coherent system out of the right building blocks, organized the way a real production system actually gets organized? That's the skill this repo demonstrates.

## The 3-layer pattern

This repo is built the same way I actually structure agentic systems, not a generic repo layout:

- **Layer 1: Directive** (`directives/`). SOPs in Markdown. Define what a "signal" is, what counts as a qualified fit, what evidence a research dossier needs, how a channel gets chosen, how a reply gets classified, how the lead record stays clean, when spend is allowed, and how the system learns from outcomes. These are policy, not code: they're the "what and why."
- **Layer 2: Orchestration** (`.claude/skills/`). One skill per pipeline stage. Each skill reads the relevant directive, calls the relevant execution script where one exists, and does the judgment work (research, drafting, classification) a deterministic script can't do. This is the "how a session actually runs it, step by step."
- **Layer 3: Execution** (`executions/`). A handful of small, deterministic Python scripts for the pieces that genuinely shouldn't be re-reasoned by an LLM every time: an ICP scoring formula, a spend-gate check, a single-writer record update. Illustrative, not a working pipeline: no live API calls, no real credentials.

## System shape

Five pipeline stages, plus three cross-cutting controls that sit underneath the whole flow rather than living in one stage:

1. **Signals come in** → `signal-harvest`
2. **Bad fit gets filtered** → `icp-qualify`
3. **The lead is researched** → `signal-research-dossier`
4. **Outreach is staged** → `outreach-draft-and-send`
5. **Replies become pipeline** → `reply-to-pipeline`

Controls: **CRM stays current** (`system-of-record-sync`), **Cost control** (`spend-and-cost-guard`), **Learning loop** (`campaign-learning-loop`). Approval-before-sends isn't a separate skill: it's a gate built into stages 4 and 5, the same way it's a gate in the real system rather than a bolt-on.

See `README.md` for the full architecture diagram, the skill table, and exactly which real public Claude Code skill pattern each stage was adapted from.

## Operating principles

1. **Evidence before spend.** Every paid step (enrichment, deep research) sits behind a cheap deterministic pre-check. This mirrors a real fix I shipped in the production system: a research-readiness gate that only re-checks fit for leads that never had a real qualification decision, not leads that already cleared one upstream.
2. **Autonomous inside the job, gated at the edge.** Scoring, research, and drafting run freely. Sends, CRM writes, and spend cross an explicit approval gate.
3. **One writer, always a reason.** Every record update goes through a single function that logs why, not ad-hoc field edits scattered across the system.
4. **Integrations are stated, not wired.** Every skill names the real tool it would connect to in production. None of it is live here.
5. **Say when a pattern doesn't exist.** Where I couldn't find a real external skill implementing a mechanic, the skill says so directly instead of inventing a source.

## File map

- `directives/`: the 8 policy SOPs (Layer 1)
- `.claude/skills/`: the 8 orchestration skills (Layer 2)
- `executions/`: 3 illustrative deterministic scripts (Layer 3)
- `context/icp.md`: the fictional ICP this system qualifies against
- `context/example-leads.md`: the fictional lead batch used across every skill's worked example
- `context/decisions-log.md`: fictional seeded decisions showing the skills in use

## Worked example

Every skill's worked example runs against the same fictional lead batch (`context/example-leads.md`): six software companies, hero lead **Nova Systems Lab**: the same fixture data used in the real Outbound demo video, for continuity between this repo and the demo.
