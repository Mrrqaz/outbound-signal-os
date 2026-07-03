# System of Record

**Status:** Policy (Layer 1). Read by `.claude/skills/system-of-record-sync/SKILL.md`.
**Owner:** Outbound Signal OS.

## Purpose

Every other skill in this repo reads and writes lead state. This directive is what keeps that state trustworthy: one identity per company, one writer, always a reason.

## One identity, dedup on import

Before any new lead enters the system, check for an existing record for the same company (matched on domain, primary company identifier, or an equivalent stable key). On a match, annotate the existing record instead of creating a duplicate. Duplicate records are how two skills end up working the same company without either one seeing the other's history.

Deduplication prefers a stable identifier (domain) over a fuzzy one (company name string match): domain matches are reliable, name matches have a real false-positive rate and should be flagged for a human decision rather than auto-merged.

## Single-writer, reason-coded updates

Every field update on a lead record goes through one write function, and every call to it carries a short reason (which skill made the change, and why). No skill edits a lead field directly outside that function. This is what makes the record auditable after the fact: a human (or another skill) can look at any lead and see not just its current state, but why it got there.

## Suppression is global

A suppression decision (see `reply_handling.md`'s cross-channel rule) is a property of the lead record, not of one channel's state. Every skill checks the record's suppression flag before acting, regardless of which channel it's about to use.

## Hygiene scoring

Periodically score the overall record set for hygiene: duplicate rate, missing-field rate, stale-record rate. A hygiene score isn't a one-time audit: it's a recurring check that catches drift before it compounds. See `.claude/skills/system-of-record-sync/SKILL.md` for the scoring approach.

## What this directive does not cover

What counts as a signal or a qualified lead in the first place (`signal_sourcing.md`, `icp_filtering.md`).
