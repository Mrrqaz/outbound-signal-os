---
name: signal-research-dossier
description: Take a TIER_1 or TIER_2 lead handed off from icp-qualify and go beneath its first visible signal, run the account-state, company-intelligence, signals-and-timing, and org/people research dimensions, apply the minimum-evidence standard so no lead reaches outreach on one uncorroborated signal, synthesize a specific why-now angle, separate safe claims from avoid claims with a proof URL on every claim, and recommend a channel and tone. A thin dossier holds the lead instead of forcing it forward. Run after a lead clears icp-qualify, or when asked to "research this lead," "build the dossier for [company]," "find the why-now angle," or "check if this lead has enough evidence to reach out."
user_invocable: true
---

# Signal Research Dossier

Adapted from amplemarket/skills' `skills/torpedo/SKILL.md` (github.com/amplemarket/skills, official Amplemarket org, 4 stars / 1 fork): the phased workflow this skill borrows from is Phase 1's four parallel research dimensions (existing account state, company intelligence, **signals & timing**, meaning job postings, funding, leadership changes, product launches, news, 10-K filings, and LinkedIn activity, plus org-chart/people mapping), and Phase 2's angle-synthesis pattern, quoted directly: "2 well-supported angles beat 5 vague ones," plus its anti-fabrication rule, also quoted directly: "Don't fabricate facts, angles, hooks, or connections that aren't verified or feel too farfetched." Also informed by sachacoldiq/ColdIQ-s-GTM-Skills (189 stars / 67 forks), whose Signal Sourcer master skill and its 9 sub-skills (job-changes, funding, hiring, tech-changes, and a multi-signal scoring framework with tiers and thresholds) are the closer analog for "corroborate beyond the first signal," though it's a signal-detection toolkit, not a full dossier compiler, and doesn't produce the angle/claims/route output this skill does. One honest addition on top of both sources: torpedo does not require a literal, formatted proof-URL field per claim in its output. The "every claim traces to a real source link" requirement below is my own addition, layered onto its anti-fabrication rule, not sourced from either repo.

A lead that reaches outreach on one signal alone gets a generic pitch. "I saw you're hiring SDRs" is the line every vendor watching that job board sends the same week. This skill exists so outreach never fires on a single, uncorroborated data point, it goes underneath the first visible signal, finds at least one more piece of real evidence that the moment is genuine, and compiles that evidence into a dossier with a specific why-now angle, not a template with a company name dropped in.

## Operating Rules (read first)

- **The minimum evidence standard is a gate, not a suggestion.** Per `directives/research.md`, a lead does not proceed to outreach on one signal alone. If research turns up nothing beyond the original signal, the dossier says so honestly and the lead is held, it is not padded to look complete.
- **Never fabricate a fact, angle, or connection.** If two findings don't actually connect (a hiring signal and an unrelated news item that happen to be near in time), don't invent a causal story between them. State what's there; keep the angle as modest as the evidence supports.
- **Every claim traces to a real source URL.** No source link, no claim in the safe-claims list. This is the one requirement in this skill that goes beyond what torpedo itself specifies (see the citation above).
- **Safe claims and avoid claims are not the same list with different labels.** A safe claim is something the evidence directly supports saying to the lead. An avoid claim is something the evidence only implies, inference is not confirmation, and `outreach.md`'s drafting rules only let the next stage draft from the safe list.
- **This skill inherits the cost gate, it doesn't re-check it.** `directives/cost_control.md` already required a lead to clear `icp-qualify` before any paid research step runs. A lead arriving here has already cleared that gate, don't re-litigate fit, research the signal.
- **A thin dossier is a hold decision, not a failure to fix by writing more.** Padding a thin dossier with speculative detail to make it look thorough is the exact failure mode `directives/research.md` warns against.
- **A held lead is not a dead lead.** Holding at Step 3 means the lead sits available for re-research the next time a fresh signal appears on it. Don't treat a hold as closing the record.

## Intended Integrations (not live in this demo)

- **A semantic web-research provider** (Exa, Tavily, or an equivalent) would power the search behind Step 2's signals-and-timing and company-intelligence dimensions, finding funding mentions, news, and leadership changes instead of relying on whatever is pasted in.
- **A page-extraction tool** (Apify's actors, Firecrawl, or an equivalent) would pull clean page content from a company site or press release once a candidate source URL is found, so the proof-URL requirement in Step 5 points at real, parseable content.
- **An enrichment waterfall** (**Prospeo** for email discovery, **Apollo** for contact and company data, **Floqer** orchestrating the fallback across providers) would fill Step 2's org/people-mapping dimension, verifying the contact, role, and reachable path the route recommendation in Step 6 depends on, instead of scoring off whatever public detail already happens to be on the record.
- **A WebSearch/web-research MCP** would do the general query fan-out this skill's four dimensions need, across job boards, funding databases, and LinkedIn activity.
- **A CRM/system-of-record read** (the sync target of `directives/system_of_record.md`) would power Step 2's account-state dimension, so research never starts blind on a lead the system has already touched.
- **A spend-tracking hook** (`directives/cost_control.md`'s per-lead cumulative spend log) would record this stage's research cost against the lead's running total the moment a paid tool actually ran, so spend-proportional-to-quality stays measurable, not just budget-within-range.
- None of these are wired into this repo. This is a demonstration of the research and evidence-gating logic. Right now this skill runs on whatever is pasted in or already on the lead record from `context/example-leads.md`, and states plainly when a step would depend on a live integration it doesn't have.

## Step 1: Pull the Lead and the Original Signal

Take the lead as handed off from `icp-qualify`: company, contact name and role, the original signal, the tier (TIER_1 or TIER_2 only, see `directives/icp_filtering.md`), and the ICP score. TIER_3 and TIER_4 leads don't reach this skill, they're held or deprioritized upstream. Note what's already known so Step 2 isn't re-deriving fit, this skill's job is corroboration and angle-building, not re-qualification.

If any of these fields is missing from the handoff (no tier, no recorded signal text), that's a process gap worth flagging before research starts, not something to infer from the company name.

## Step 2: Run the Four Research Dimensions

Adapted from torpedo's Phase 1. Run all four, even when one looks unnecessary for this lead, a thin result on any dimension is itself information:

1. **Account state**: has this company or contact touched the system before (prior outreach, a prior reply, a note on record)? Prevents redundant re-research and a second team member accidentally re-pitching a live thread.
2. **Company intelligence**: business model, market position, size, funding stage. Cross-check against `context/icp.md`'s fit criteria, not to re-score fit, but to make sure the angle being built doesn't contradict something already known about the company.
3. **Signals & timing**: the dimension that matters most for Step 3. Look for anything beyond the original signal: a second job posting, a funding mention, a leadership change, a product launch, relevant news. This is the corroboration `directives/research.md`'s minimum evidence standard is checking for.
4. **Org/people mapping**: is the contact positioned to actually feel the pain the signal implies, and is there any public activity (a LinkedIn post, an interview, a company blog byline) that supports a personalized angle or informs the route recommendation in Step 6.

## Step 3: Apply the Minimum Evidence Standard (gate)

Check Step 2's findings against `directives/research.md`'s rule: at least one corroborating data point beyond the original signal, found in any of the four dimensions, most often dimension 3.

- **Corroborated** (two or more independent, evidence-backed findings): the dossier proceeds to Step 4.
- **Thin** (only the original signal, nothing else found): stop here. Mark the dossier thin, say so plainly, and hold the lead rather than force it forward. A held lead isn't dropped, it can re-enter if a new, stronger signal appears later, the same held-not-deleted principle `directives/icp_filtering.md` applies to sub-threshold leads.

## Step 4: Synthesize the Why-Now Angle

Combine the corroborated findings into one specific, dated, causal angle, not a list of facts. Per torpedo's Phase 2 pattern, one well-supported angle beats several vague ones, don't manufacture a second or third angle just to look thorough if the evidence only cleanly supports one. If the findings don't actually connect (unrelated events that happen to be close in time), don't force a causal link between them, state the two facts and keep the angle proportionally modest.

## Step 5: Separate Safe Claims from Avoid Claims, and Attach Proof URLs

For every fact behind the angle, decide: **safe** (the evidence directly supports saying this to the lead) or **avoid** (the evidence only implies this, don't state it directly, it's inference). Attach the real source URL to every safe claim. A finding with no traceable source doesn't make the safe-claims list, no matter how well it fits the angle.

## Step 6: Recommend the Route

Match the dossier to `directives/outreach.md`'s channel rules using what Step 2's org/people mapping found: LinkedIn or email as the primary channel for most leads; WhatsApp only where prior context makes it appropriate, never the default first touch; a resource offer only when the angle genuinely supports one being useful, not as homework attached to every dossier.

## Step 7: Complete the Dossier and Hand Off

Assemble the final dossier in `directives/research.md`'s five fields: signal summary, why-now angle, proof URLs, safe claims vs. avoid claims, route recommendation. If the lead cleared Step 3's gate, hand off to `outreach-draft-and-send`. If it didn't, the dossier's output is the hold decision itself, log why, and stop, nothing advances downstream.

Either outcome writes through `executions/lead_record_writer.py`'s single write path, not an ad-hoc field edit. The record update carries a reason string (per the repo's single-writer-always-a-reason principle), for example `research_status: complete, reason: "signal-research-dossier completed with 2 corroborating signals"`, or `research_status: held, reason: "signal-research-dossier found no corroboration beyond the original signal"`.

## Worked Example (fictional)

**Lead:** Nova Systems Lab, hero lead from `context/example-leads.md`. Contact: Maya Patel, Head of Sales. Original signal: hiring SDRs (public job listing, sourced by `signal-harvest`). Tier: TIER_1, ICP score 88.

**Step 2, four dimensions:**
1. Account state: no prior Autoage/Nova contact on record. First touch.
2. Company intelligence: enterprise data-infrastructure software company, roughly 140 employees, within the ICP's 20-500 band.
3. Signals & timing: the careers page now shows three open SDR roles, all reporting to Maya, up from the single listing `signal-harvest` originally sourced. A second, independent finding corroborates it: Maya posted publicly on LinkedIn ten days ago about "doubling our outbound motion this quarter."
4. Org/people mapping: Maya Patel is publicly active on LinkedIn, that post is the corroborating finding above, and it also informs the route recommendation below.

**Step 3, evidence gate:** two independent findings (the hiring signal, now three open roles, plus Maya's own public statement about the reason behind it), not one. **Corroborated.** Proceeds.

**Step 4, why-now angle:** Nova Systems Lab is actively building a new SDR team under Maya right now, a narrow window before those hires are ramped and the outbound process is already locked in. One well-supported angle, not stacked with weaker secondary angles.

**Step 5, safe claims / avoid claims:**
- Safe: "three open SDR roles posted in the last two weeks, reporting to the Head of Sales" (source: `https://example.invalid/jobs/nova-systems-lab-sdr`, careers page).
- Safe: "Maya posted publicly about scaling outbound this quarter" (source: `https://example.invalid/linkedin/maya-patel-post`, LinkedIn).
- Avoid: don't state or imply Nova has no outbound system today, or is struggling, that's inferred from the hiring surge, not something either source actually says.

**Step 6, route:** Maya Patel is LinkedIn-active per Step 2's org mapping, so LinkedIn is the primary channel; a verified work email on file supports email as a secondary channel. A resource offer isn't recommended for this touch, a full asset on a cold open would read as homework here, that's a call for `outreach-draft-and-send`'s own channel-fit step to revisit if Maya engages, not a default this dossier forces. WhatsApp isn't recommended either, there's no prior relationship.

**Step 7, handoff:** dossier is complete and corroborated. Hands off to `outreach-draft-and-send` with the angle, the two safe claims and their URLs, the one avoid claim, and the LinkedIn-plus-email route. The record write carries the reason `"signal-research-dossier completed with 2 corroborating signals"`, matching the exact update `executions/lead_record_writer.py` runs for this lead.

**Contrast (what a thin result looks like):** if Step 2 had turned up nothing beyond the SDR listing itself, for example on a supporting-batch lead like QueryForge Cloud, TIER_2 at 72%, the dossier would stop at Step 3, say plainly that only the original signal was found, and hold the lead rather than manufacture a second angle to look complete.

## Rules

- Never advance a lead to outreach on one signal alone. The minimum evidence standard requires at least one corroborating data point beyond the original signal, every time, no exceptions for a high ICP score.
- Don't fabricate a fact, angle, or connection that isn't verified, even if it would produce a sharper pitch. Two well-supported angles beat five vague ones.
- Every claim in the dossier traces to a real source URL. A claim without a link doesn't go in the safe-claims list.
- Distinguish what the evidence supports saying directly (safe claims) from what it only implies (avoid claims). Outreach only drafts from the safe list.
- A thin dossier is a signal to hold the lead, not a reason to pad it with invented supporting detail. Held is not deleted, a new signal can bring the lead back.
- The route recommendation follows `directives/outreach.md`'s channel rules, not every lead gets every channel, and WhatsApp is never the default first touch.
- If a research dimension in Step 2 comes back empty (no account history, no people data), say so in the dossier rather than silently omitting the section.
