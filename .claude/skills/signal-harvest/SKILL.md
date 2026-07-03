---
name: signal-harvest
description: Scan public sources for buying signals tied to sales or GTM capacity (job postings, funding announcements, tech-stack changes, growth/expansion, public pain points), classify each into the HIRING/FUNDING/TECHNOLOGY/GROWTH/PAIN taxonomy with a HIGH/MEDIUM/LOW strength rating and a one-sentence outreach angle, then assemble a strength-sorted batch ready for icp-qualify. Run at the start of every harvest cycle, when a target list needs a fresh signal pass, or when asked to "find signals for these companies," "run a harvest," or "check whether this listing is still live."
user_invocable: true
---

# Signal Harvest

A target list without a fresh signal is just a list of names someone matched on size and industry six months ago. Reaching out on fit alone produces the same generic "noticed you're a growing company" line every other tool in the prospect's inbox already sent. This skill exists so outreach starts from something that actually changed recently, dated and sourced, not a static match nobody re-checked. Without it, everything downstream (`icp-qualify`, research, drafting) either has no real "why now" to work with, or trusts a signal that quietly went stale weeks ago.

Adapted from janskuba's `outbound-agents` repo (github.com/janskuba/outbound-agents, 74 stars, 25 forks), `.claude/agents/signal-scraper.md`. That agent's design is the source of the 5-type taxonomy (HIRING, FUNDING, TECHNOLOGY, GROWTH, PAIN), the HIGH/MEDIUM/LOW strength rating per finding, the one-sentence recommended outreach angle attached to each signal, the strength-descending sort, the NONE/LOW fallback row when nothing is found, and the CSV auto-enrichment trigger when 3 or more of 8 required fields come back empty. Secondary source: openfunnel/openfunnel-skills (github.com/openfunnel/openfunnel-skills, 7 stars), skill `spot-companies-hiring-to-solve-specific-problems`, which frames a newly posted job req as a proxy for an active, budgeted pain point, re-run daily rather than sourced once. This version ports both mechanics into an operator-OS shape (explicit steps, worked example, stated-not-wired integrations) for the Nova Systems Lab demo. See `directives/signal_sourcing.md` for the full signal taxonomy and source-priority rules this skill implements.

## Operating Rules (read first)

- **HIRING is the priority scan, not one option among five.** It is public, dated, and implies budget. Always work the job-board and career-page scan in Step 2 before dropping to a weaker source, and do not let a lower-priority signal substitute when a HIRING signal was available and never checked.
- **A signal needs a dated, checkable source.** "They seem like they are growing" is not a signal, it is a guess. If a finding cannot be tied to a posted date and a source (a listing URL, a press release, a filing), it does not enter the batch as a rated signal.
- **PAIN signals never stand alone.** Per `directives/signal_sourcing.md`, PAIN is the weakest signal type with the highest false-positive rate. A PAIN finding with no corroborating signal (another type present on the same company, or a second independent mention) caps at LOW with a corroboration-needed flag, never HIGH or MEDIUM on its own.
- **The 30-day freshness rule is explicit for HIRING and FUNDING only.** Past 30 days, re-verify the listing or announcement is still live before it carries a HIGH or MEDIUM rating. TECHNOLOGY, GROWTH, and PAIN carry no hard cutoff in the directive, so age is a soft factor in the strength table (Step 3), not an automatic invalidation.
- **Collect into a batch, not one-off.** A single sourced company does not get pushed downstream by itself. `icp-qualify` expects the full harvest cycle's results (Step 7), not a trickle of individual rows.
- **This skill does not decide fit.** A HIGH-strength signal on an obviously out-of-ICP company still gets a row in the batch. Fit is `icp-qualify`'s job against `context/icp.md`, not this skill's. Do not quietly drop or promote a row on a fit judgment made here.
- **Never fabricate a source URL, a posted date, or a contact detail.** If a required field cannot be found, leave it empty and let Step 5 catch it. Do not fill it with something plausible-sounding to make a row look complete.

## Intended Integrations (not live in this demo)

- **A job-board API or scraping tool** (for example Apify's job-listing actors, or direct career-page scraping) would power Step 2's HIRING scan with live, dated listings instead of whatever has already been logged from a prior pass.
- **A public funding-database API** (for example Crunchbase or PitchBook) would power the FUNDING scan and let Step 4's freshness check run against a confirmed announcement date instead of an estimate.
- **A companies-house-style registry** (for example UK Companies House, or an equivalent incorporation and filings registry elsewhere) would corroborate that a company is still active, useful before spending a harvest slot on one that has dissolved or gone dormant.
- **A general web-search or news API** would power the sparse-record enrichment trigger in Step 5, running a targeted search per company when too many required fields are empty instead of leaving the row incomplete.
- None of these are wired into this repo. This is a demonstration of the classification and batching logic. Right now this skill runs on the fixture batch in `context/example-leads.md`, or on whatever company and signal data is pasted in, and it says so plainly whenever a step depends on a live integration it does not have.

## Step 1: Pull the Target List

Take the company list as given: a CSV of names carried forward from a prior cycle, a saved account list, or, for this demo, the fixture batch in `context/example-leads.md`. Note what is already on file per company (a prior signal, a prior harvest date) versus what is a fresh entry with nothing logged yet. A company with a signal logged more than 30 days ago is not skipped or assumed still current, it goes through Step 4's re-verification like everything else.

## Step 2: Scan Sources in Priority Order

Per `directives/signal_sourcing.md`, work structured sources before unstructured ones: (1) job boards and company career pages, (2) funding databases, (3) general news and press, (4) social platforms. Stop escalating once a HIGH-strength signal is confirmed for a company, a confirmed job posting does not need a LinkedIn post to back it up. If the structured tiers turn up nothing, continue to social platforms before concluding there is no signal (Step 6), since PAIN findings mostly live there.

## Step 3: Classify Each Finding

Sort every finding into exactly one of the five types and rate it HIGH, MEDIUM, or LOW:

| Type | HIGH | MEDIUM | LOW |
|---|---|---|---|
| HIRING | Live GTM/revenue role (SDR, AE, Head of Sales, RevOps) posted within 14 days | Live GTM/revenue role posted 15-30 days ago, or a demand-adjacent role (marketing, CS) | A single generalist hire with no clear revenue tie, or an unverified listing 31-60 days old |
| FUNDING | Seed through Series C round announced within 30 days, amount disclosed | Round announced 31-90 days ago, or amount undisclosed | Unconfirmed raise rumor, or outside the ICP funding band per `context/icp.md` |
| TECHNOLOGY | A new GTM/revenue tool detected in the last 30 days (a job posting names the stack, a dated integration or case study) | Tool change inferred from an older job posting or one indirect mention | Guessed from a logo or badge with no dated evidence behind it |
| GROWTH | Confirmed headcount growth or a new office/market opening announced within 30 days | Growth implied by multiple simultaneous job postings across departments, no explicit announcement | A single vague post implying growth with nothing dated or checkable |
| PAIN | Never HIGH alone, see Operating Rules; corroborated by a second signal it can reach MEDIUM | A specific, dated complaint or review naming the actual gap, not generic negativity | A vague or single unconfirmed complaint with no corroboration |

Attach a one-sentence recommended outreach angle to every signal that clears LOW, naming the specific evidence (the role, the round, the tool, the expansion, the complaint). A signal without an angle attached is not finished being classified.

## Step 4: Apply the Freshness Window

For HIRING and FUNDING: actionable within 30 days of the posted or announced date. Past that, re-verify the listing or announcement is still live before it is allowed to carry a HIGH or MEDIUM rating, an unverified stale signal demotes to LOW and gets flagged `needs re-verification` rather than dropped outright, so the next harvest cycle can pick it back up. For TECHNOLOGY, GROWTH, and PAIN: the directive sets no hard cutoff, so age is only the soft factor already built into the Step 3 table.

## Step 5: Handle Sparse Records

Every signal row needs 8 fields: company name, contact name, contact role, signal type, signal strength, signal date, source citation, outreach angle. When 3 or more of these are empty after Steps 2-4, flag the row for enrichment instead of pushing it downstream half-filled. In production this fires the targeted web search named in Intended Integrations. In this demo it means writing "insufficient data, needs enrichment" instead of guessing a contact name or role that was never actually sourced.

## Step 6: No-Signal Fallback

If a company clears the source scan with nothing dated and checkable found, that is a real outcome, not a failure of the process. Do not drop the company silently from the batch. Emit a single row rated NONE/LOW so the company stays visible for the next harvest cycle instead of quietly disappearing from tracking.

## Step 7: Assemble and Sort the Batch

Compile every row from this cycle, one row per signal rather than one row per company, since a single company can carry more than one finding. Sort strength descending (HIGH, then MEDIUM, then LOW/NONE). This batch is the handoff artifact: it feeds directly into `icp-qualify`, which checks each row against `context/icp.md` and decides which rows are worth researching further. Signal-harvest's job ends at "here is what changed and how strong the evidence is," it does not decide who is worth pursuing.

## Worked Example (fictional)

Harvest cycle 2026-06-28, target list pulled from `context/example-leads.md`.

**Nova Systems Lab**
Step 2: the career-page scan (tier 1) finds a live "SDR, Outbound" listing posted 2026-06-19, 9 days before this cycle.
Step 3: HIRING, live GTM role posted within 14 days, HIGH. Angle: "They have an open SDR req reporting to Maya Patel, Head of Sales, and no visible outbound system feeding it yet, reference the specific req, not a generic 'hiring' line."
Step 4: 9 days old, well inside the 30-day window, no re-verification needed.
Step 5: all 8 fields present, no enrichment trigger.
Row: Nova Systems Lab, HIRING, HIGH, 2026-06-19.

**QueryForge Cloud**
Step 2: career-page scan finds an "Account Executive" listing posted 2026-06-02, 26 days before this cycle.
Step 3: HIRING, live GTM role posted 15-30 days ago, MEDIUM, not HIGH, the freshness edge is what pulls it down a tier.
Step 4: 26 days old, still inside the 30-day window but close to the edge, flagged for an early re-check next cycle rather than treated as stale now.
Step 5: all 8 fields present, no enrichment trigger.
Row: QueryForge Cloud, HIRING, MEDIUM, 2026-06-02.

**RelayDesk AI**
Step 2: the only thing on file is a "Hiring growth leadership" signal logged 2026-05-15, 44 days before this cycle. No fresh listing turns up on this pass.
Step 4: 44 days old crosses the 30-day HIRING window, re-verification is required before it can keep a HIGH or MEDIUM rating. The career-page re-check comes back empty, the listing appears closed. Demoted to LOW and flagged `needs re-verification`.
Step 5: contact (Leah Morgan, Founder) and company name are present, but signal date and source citation are now stale and unconfirmed, 2 of 8 fields effectively invalid. That is below the 3-field enrichment trigger, so the row stays a flagged LOW rather than escalating to enrichment.
Row: RelayDesk AI, HIRING, LOW (needs re-verification), 2026-05-15 (stale).

**Batch output, sorted strength descending:**

1. Nova Systems Lab, HIRING, HIGH, 2026-06-19
2. QueryForge Cloud, HIRING, MEDIUM, 2026-06-02
3. RelayDesk AI, HIRING, LOW (needs re-verification), 2026-05-15

The remaining three fixture companies (StackPilot Software, OpsLayer CRM, BeaconDesk SaaS) run the same three steps and join the same batch. This full batch hands off to `icp-qualify` next, which checks every row against `context/icp.md` and decides which ones justify a research dossier.

## Rules

- Never log a signal without a dated, checkable source. A guess is not a signal, no matter how plausible it sounds.
- HIRING and FUNDING signals expire at 30 days without re-verification. Do not keep using a stale "why now" that may have quietly gone false.
- PAIN never carries a HIGH or MEDIUM rating alone. It needs corroboration from a second signal or a second independent mention.
- A company with nothing found still gets a row. Silent disappearance from the batch is a bug, not a clean pass.
- This skill classifies and rates. Fit decisions belong to `icp-qualify`, do not drop a row here because it looks like a bad fit.
- If 3 or more of the 8 required fields are empty, flag the row for enrichment instead of guessing a value to complete it.
- The output is a batch, sorted strength descending, not a single best lead. `icp-qualify` needs the whole cycle's results, not just the top row.
