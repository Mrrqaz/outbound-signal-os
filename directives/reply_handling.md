# Reply Handling

**Status:** Policy (Layer 1). Read by `.claude/skills/reply-to-pipeline/SKILL.md`.
**Owner:** Outbound Signal OS.

## Purpose

Classify every inbound reply, decide what happens next, and carry a positive reply through to a booked meeting: without ever auto-sending a reply that hasn't been approved.

## Classification taxonomy

Every reply gets one label: `positive_interested`, `positive_soft`, `positive_referral`, `neutral_question`, `negative_notnow`, `negative_notfit`, `negative_hostile`, `unsubscribe`, `ooo`, `bounce`, or `other`. See `.claude/skills/reply-to-pipeline/SKILL.md` for the classification logic.

## Cross-channel suppression (non-negotiable)

A hard-negative (`negative_hostile`) or opt-out (`unsubscribe`) signal on **any** channel suppresses outreach on **every** channel for that lead: not just the channel it arrived on. A lead doesn't experience this system as a set of separate channels; they experience it as one entity contacting them, and a hard no on one channel is a hard no, period. This directive exists because an early version of this system missed exactly this case. See `context/decisions-log.md`, 2026-06-28.

`negative_notnow` and `negative_notfit` are soft negatives: they pause outreach on this lead but do not suppress every channel and do not block the lead from re-entering the pipeline later if a strong new signal appears.

## Reply drafting

A reply to a `positive_*` or `neutral_question` label is drafted grounded in the original dossier (`research.md`) and any resource already offered: never a generic acknowledgment. Every drafted reply queues for the same approval gate as outbound (`outreach.md`) before it sends.

## Booking

A confirmed positive reply that agrees to a meeting is carried to a calendar booking as the close. This is the intended end state of the pipeline for a converted lead: stronger than ending on "reply logged."

## What this directive does not cover

How the underlying lead record gets updated once a reply is handled (`system_of_record.md`).
