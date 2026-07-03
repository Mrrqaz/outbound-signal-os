# Learning Loop

**Status:** Policy (Layer 1). Read by `.claude/skills/campaign-learning-loop/SKILL.md`.
**Owner:** Outbound Signal OS.

## Purpose

Outreach copy that never gets tested never improves past a guess. This directive governs how the system compares variants, decides a winner, and persists what it learned so future generation cycles don't re-discover the same insight from scratch.

## Statistical rigor

- Pre-declare the success metric and the sample size needed before a test starts. Don't decide "this looks like enough data" partway through: that's how noise gets mistaken for a real result.
- Don't peek and stop early. Stopping a test the moment it looks favorable is the single most common way a fluke gets promoted to "the winner."
- A result needs to clear a defined significance threshold on a minimum cohort size before it counts, not just show a favorable-looking raw percentage.

## Promotion requires a human decision

Clearing the significance gate makes a variant *eligible* for promotion: it does not promote it automatically. A statistically significant result on a thin cohort can still be a fluke; the human glance before cutover is what catches "this only won because of one outlier reply." See `context/decisions-log.md`, 2026-06-24.

## Persisted learnings

Every completed test writes a short structured entry to a persistent learnings log: what was tested, the result, and, critically, the **reusable pattern**, not just the raw win/loss. The pattern field is what a future test-design pass reads before proposing a new hypothesis, so the system doesn't re-run a test whose answer is already known.

## What gets tested

One variable at a time. A test that changes subject line and body copy and CTA simultaneously can't attribute the result to any one of them. See `context/decisions-log.md`, 2026-07-01 (open item on subject-line vs. body-copy variant granularity).

## What this directive does not cover

How outreach drafts get generated in the first place (`outreach.md`): this directive only covers how variants of that output get compared.
