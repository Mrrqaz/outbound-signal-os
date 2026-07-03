---
name: system-of-record-sync
description: Dedupe every incoming lead against existing records before it enters the system, route every field update through one reason-coded writer function, keep suppression state global across every channel, and periodically score the record set for hygiene (duplicate rate, missing-field rate, stale-record rate) as a graded, severity-ranked punchlist. Not a single pipeline stage, every other skill in this repo reads and writes lead state through this one. Run it whenever a new lead is about to be imported, before any skill writes a field update, when a suppression decision needs to be checked or applied, or when asked to "check for duplicates," "run the hygiene score," "is this lead suppressed," or "why does this lead have two records."
user_invocable: true
---

# System of Record Sync

A lead record that drifts (a duplicate the dedup check missed, a field two skills wrote to directly and disagreed on, a suppression flag that only applied on one channel) doesn't fail loudly. It fails quietly, for months, until someone re-contacts a lead who already said no, or two skills work the same company without either one seeing the other's history. This skill exists to make that failure mode structurally hard, not to catch it after the fact.

Adapted from `TomGranot/hubspot-admin-skills` (github.com/TomGranot/hubspot-admin-skills, 48 stars, 32 skills, confirmed by direct fetch): `merge-duplicate-companies` for the domain-first, name-fallback dedup logic and its "never merge automatically, always a human decision" rule; `suppress-global-unsubscribes` for the optout-detection-plus-audit-export pattern Step 3 draws on. The hygiene-scoring mechanic in Step 4 is adapted separately from `elijeangilles/revops-skills` (github.com/elijeangilles/revops-skills, 6 stars): `salesforce-revops-audit`'s graded A-F health report and `pipeline-hygiene-audit`'s severity-ranked, per-issue punchlist.

The single-writer, reason-coded update function in Step 2 is my own design. No real external Claude Code skill implementing exactly that mechanic turned up during research, and I'd rather say that plainly than dress up TomGranot's pattern as something it isn't. What I found was audit-before-action: snapshot the record before and after a change, export it to a CSV, so a human can review what a merge or a suppression did. What I built takes that one step further: instead of snapshotting around an action, gate the action itself behind one function that always logs why, before the write happens rather than reconstructing it after. That's a deliberate architecture choice, not a shortcut, and it's the one I'd defend if asked why the record layer looks the way it does.

## Operating Rules (read first)

- **Domain match is the only automatic dedup trigger.** A name-only match ("Nova Systems Lab" vs. "Nova Systems Lab Inc") gets flagged for a human merge decision, never auto-merged. Name-string matching has a real false-positive rate, auto-merging on it trades one data problem for a worse one: silently combining two different companies.
- **No skill in this repo edits a lead field directly.** Every update, from every stage, goes through `apply_lead_update()` in `executions/lead_record_writer.py` and carries a reason string naming which skill made the change and why. That reason string isn't decoration, it's the only thing that makes the record auditable after the fact.
- **Suppression is a property of the lead, not the channel.** Once `reply-to-pipeline` flags a lead `negative_hostile` or `unsubscribe` (see `directives/reply_handling.md`), every skill in this repo checks that flag before acting, including a different skill about to use a different channel. A suppressed lead doesn't get a pass because the next touch was going to be email instead of LinkedIn.
- **This isn't a single pipeline stage.** It's the control every other skill routes lead-record reads and writes through: `signal-harvest` calls it on import, `icp-qualify` and `signal-research-dossier` call it on every field update, `reply-to-pipeline` calls it on suppression and stage changes. Treat it as infrastructure the rest of the system depends on, not a step that runs once and hands off.
- **Hygiene scoring is recurring, not a one-time audit.** Run it on a cadence (weekly, or after a large import) and compare against the prior score if one exists. A static number with no trend doesn't say whether the record set is getting better or worse.
- **Never fabricate a dimension the source data can't support.** If a required timestamp field isn't present, say the stale-record dimension is unscored this run. Don't estimate one just to produce a clean-looking blended grade (see `directives/system_of_record.md`).
- **The `caller` argument names a real skill, not a generic label.** `signal-harvest`, `icp-qualify`, `reply-to-pipeline`, whichever skill actually made the call. A vague caller like `"system"` defeats the point of the audit log, the whole reason it exists is to answer "which skill did this, and why" without guessing.

## Intended Integrations (not live in this demo)

- **A structured database** (a NocoDB- or Airtable-style backend) would replace the in-memory `RECORDS` dict in `executions/lead_record_writer.py` as the actual store. `apply_lead_update()` would run as a database write instead of a dict mutation, but the gate stays identical: dedup check first, one writer, mandatory reason. That's the point of putting the pattern in a standalone function instead of inline in each calling skill.
- **A scheduled job** (cron, or this repo's own scheduling layer) would run Step 4's hygiene score automatically on a cadence instead of on request, and diff it against the prior run so drift shows up as a trend, not a one-off number.
- **A Slack or email alert** would fire the moment a domain-match collision gets blocked pending human merge decision (Step 1), or when the hygiene grade drops a full letter grade between runs, so the flag doesn't sit unread in a log.
- **An audit-log export** would turn `AUDIT_LOG` into a queryable table (filterable by caller, by company, by date range) instead of a Python list that only exists for the length of one process. This is what a real handover package would hand over: not just the current state of a lead record, but every reason it got there.
- None of these are wired into this repo. Step 1 and Step 2 run against the fixture batch in `context/example-leads.md` and the in-memory dict in `lead_record_writer.py`. Step 4 is computed by hand against that same fixture. The gate logic is what this skill demonstrates, not the storage layer underneath it.

## Step 1: Dedup Check Before Any Import

Before a new lead enters the system, normalize its website into a bare domain (strip protocol, take everything before the first `/`, see `_domain()`) and check it against every existing record's domain via `find_existing()`.

- **Domain matches an existing record under the same company name:** this is an update, not a new lead. Route it to Step 2.
- **Domain matches an existing record under a different company name string:** block the automatic insert. Raise for a human merge decision and log why, don't guess which of the two names is correct or silently keep the older one.
- **No domain match, but the company name is a close fuzzy match to an existing record** (no website given to check): flag for human review too, at lower confidence than a domain match, but still don't auto-merge. A domain match is reliable; a name-only match never is.
- **No domain match, no fuzzy name match:** genuinely new. Proceed to Step 2 as an insert.

## Step 2: Route Every Field Update Through the Single Writer

Every field write, whether it's a brand-new lead or the fortieth update to one already in the system, goes through `apply_lead_update(company, fields, reason, caller)`. Whenever the update carries a `website` field, it re-runs the Step 1 domain check before writing, so most stages that skip Step 1 directly still get caught. An update with no `website` field (a status change with nothing new to dedup against) skips that specific check, a real gap worth knowing about rather than a claimed guarantee. Either way it merges the new fields into the existing record and appends a before/after snapshot plus the reason and caller to `AUDIT_LOG`. If two skills disagree about a field's value, the audit log shows exactly which call won and why, instead of a silent overwrite nobody can trace back.

## Step 3: Enforce Global Suppression

Before `outreach-draft-and-send`, `reply-to-pipeline`, or any other skill acts on a lead on any channel, check the record's suppression flag first. A `negative_hostile` or `unsubscribe` classification (`directives/reply_handling.md`) suppresses every channel for that lead, not just the one it arrived on. `negative_notnow` and `negative_notfit` are soft: they pause outreach on this lead but don't block it from re-entering later on a new signal. Log the suppression event itself through `apply_lead_update()` before flipping the flag, the same audit-before-action discipline `suppress-global-unsubscribes` uses, applied to the write gate instead of a separate CSV export.

## Step 4: Score Record Hygiene (Periodic)

Score three dimensions against the current record set:

| Dimension | Formula | Weight |
|---|---|---|
| Duplicate rate | stored duplicate records / total records (collisions blocked at Step 1 don't count here, they're logged separately as a leading indicator) | 35 |
| Missing-field rate | records missing at least one required field (company, website/domain, signal, research status) / total records | 45 |
| Stale-record rate | records with no `apply_lead_update()` write in the last 30 days / total records | 20 |

Missing-field carries the heaviest weight on purpose: a record missing its domain doesn't just look incomplete, it breaks Step 1's dedup check for that specific record. That's a compounding risk, not a cosmetic gap.

Convert each dimension to a health score (`(1 - rate) * 100`). If a dimension can't be computed from the available data (no timestamp field, for example), leave it out and renormalize the remaining weights to still sum to 100, don't zero-fill it. Blend the scored dimensions into one number and grade it: **A** 90+, **B** 80-89, **C** 65-79, **D** 50-64, **F** under 50. Report the grade alongside a severity-ranked punchlist of what's actually driving it, per-issue, not just the number.

## Step 5: Report Findings

Surface a blocked Step 1 collision immediately, in the moment it happens, don't batch it into the next periodic report. Present the Step 4 hygiene score as a grade plus a ranked punchlist, worst issue first, each line naming the affected record count and why it matters, not just a percentage.

## Worked Example (fictional)

**Dedup check (mirrors `executions/lead_record_writer.py`'s `__main__` block exactly):**

Nova Systems Lab is already in the system with two prior writes, both logged with a caller and a reason:

1. `apply_lead_update("Nova Systems Lab", {icp_tier: "TIER_1", research_status: "pending", ...}, reason="icp-qualify scored TIER_1, queued for research", caller="icp-qualify")`
2. `apply_lead_update("Nova Systems Lab", {research_status: "complete", dossier_url: "internal://dossiers/nova-systems-lab"}, reason="signal-research-dossier completed with 2 corroborating signals", caller="signal-research-dossier")`

A second source batch then imports **"Nova Systems Lab Inc"** with website `https://example.com/nova-systems-lab`, the same domain already on file under the plain "Nova Systems Lab" record.

Step 1 catches it: domain match, different company name string. `apply_lead_update()` raises before writing anything:

```
Blocked as designed: Domain match found for an existing record (Nova Systems Lab)
under a different company name (Nova Systems Lab Inc): flag for human merge
decision, do not auto-merge on a fuzzy name match.
```

Reported per Step 5, immediately: one blocked collision, caller `signal-harvest`, reason "duplicate import attempt from a second source batch," queued for a human merge decision. Nova Systems Lab's own record is untouched, the second batch's row never overwrote anything.

**Hygiene score, full 6-lead fixture (`context/example-leads.md`):**

Duplicate rate: 0/6 stored duplicates (the collision above was blocked, not stored). Health = 100.
Missing-field rate: only Nova Systems Lab carries a website/domain and a research status in the fixture. The five supporting-batch leads (QueryForge Cloud, RelayDesk AI, StackPilot Software, OpsLayer CRM, BeaconDesk SaaS) have no domain on file. 5/6 = 83% missing at least one required field. Health = 17.
Stale-record rate: unscored this run, the static fixture has no `apply_lead_update()` timestamps to check against a 30-day window.

Weights renormalize to duplicate 43.75%, missing-field 56.25% (stale excluded). Blended score = (100 x 0.4375) + (17 x 0.5625) = 43.75 + 9.56 ≈ **53 → Grade D**.

Punchlist, worst first:
1. **[High]** 5 of 6 records have no domain on file, blocking Step 1's dedup check for every one of them. They're exposed to exactly the collision Nova Systems Lab just avoided, and none of them would be caught.
2. **[Medium]** Stale-record rate unscored, no timestamp field in this static fixture. Flag for backfill once the live database integration lands.
3. **[Info]** Duplicate rate is 0% stored, and the one blocked collision this period is the control working as designed, not a mark against the score.

## Rules

- Domain match is the only automatic merge trigger. A name-only match always routes to a human decision, no exceptions.
- No field write bypasses `apply_lead_update()`. Every call carries a reason and a caller, or it doesn't happen.
- Suppression applies to the lead across every channel the moment a hard-negative or unsubscribe lands, not just the channel it arrived on.
- Never fabricate a hygiene dimension the data can't support. Say it's unscored and renormalize the rest, don't estimate a value to force a clean grade.
- A hygiene score is a trend line, not a one-off. Compare against the prior run whenever one exists.
- This skill is infrastructure other skills call, not a stage that runs once. If a skill elsewhere in this repo appears to write a lead field directly, that's a bug in that skill, not a valid shortcut.
