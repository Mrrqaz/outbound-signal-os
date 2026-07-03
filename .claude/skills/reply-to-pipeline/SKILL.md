---
name: reply-to-pipeline
description: Classify every inbound reply to outreach from outreach-draft-and-send against an 11-label taxonomy (positive_interested, positive_soft, positive_referral, neutral_question, negative_notnow, negative_notfit, negative_hostile, unsubscribe, ooo, bounce, other), apply cross-channel suppression the moment a hard-negative or unsubscribe lands on any channel, draft a dossier-grounded reply for anything positive or a genuine question, and carry a confirmed positive reply through to a booked meeting. Run whenever a reply comes in on any outreach channel, or when asked to "classify this reply," "handle the reply from [lead]," or "why did outreach stop for [lead]."
user_invocable: true
---

# Reply to Pipeline

Turns an inbound reply into one of three outcomes: suppressed everywhere, drafted and queued for approval, or escalated to a human, and carries a confirmed positive reply through to a booked meeting. A reply that gets misclassified either burns goodwill (outreach keeps hitting someone who already said no) or drops a real buyer on the floor (a positive reply sits unanswered because nobody read it as one). This skill exists so every reply gets the same read, every time, regardless of which channel it landed on.

Adapted from growthenginenowoslawski's `coldoutboundskills` repo (github.com/growthenginenowoslawski/coldoutboundskills, 475 stars, 174 forks), skill `positive-reply-scoring`: the 11-label classification taxonomy above and the `positive_reply_rate = positive_replies / total_sent` metric are that skill's design. Worth being precise about what the source actually covers, it classifies a reply and hands off to a separate document for what happens next. It doesn't auto-pause a sequence, doesn't draft a reply, and doesn't touch a calendar.

Everything past classification in this skill, the cross-channel auto-pause on a hard no, the dossier-grounded reply draft, and the booking-through-close logic, is my own design. I looked for a real public Claude Code skill that implemented that full loop as one cohesive mechanic and didn't find one. The closest candidate I checked, louisblythe's `Sales-Skills` repo (79 stars), has skill names that gesture at this territory (`compliance-handling`, `objection-recognition`), but I couldn't confirm what mechanic actually lives inside them, so I'm not citing it as a verified source for anything here. What follows the classification step is built directly from the cross-channel suppression principle this repo already commits to in `directives/reply_handling.md`, the reasoning behind it is logged in `context/decisions-log.md` under 2026-06-28.

## Operating Rules (read first)

- **Classify before anything else happens.** No suppression, no drafted reply, no booking action fires off a raw reply. The label decides the branch, nothing downstream re-guesses intent from the text a second time.
- **A hard negative or unsubscribe on any channel suppresses every channel for that lead, not just the one it arrived on.** This is not a per-lead judgment call, it's the non-negotiable rule in `directives/reply_handling.md`. See Step 3.
- **Soft negatives pause, they don't suppress.** `negative_notnow` and `negative_notfit` stop the current sequence on this lead but leave the door open for it to re-enter the pipeline later if a strong new signal appears. Don't collapse this with hard-negative handling, they're different actions with different reversibility.
- **A drafted reply is grounded in the dossier, never a generic acknowledgment.** Every claim traces to the lead's `research.md` safe-claims list or a resource already offered. If the dossier doesn't support a claim the reply seems to invite, say less, don't invent more.
- **Nothing sends itself.** A drafted reply queues for the same human approval gate `outreach.md` requires for the first touch. Classification and drafting run automatically, sending never does.
- **A booking is the intended end state for a converted lead, not "reply logged."** Don't let this skill's job stop at classification when the reply clearly wants to move to a meeting.
- **If a reply can't be matched to an existing lead record, say so and stop.** Don't guess which lead a reply belongs to from a name or a company string alone, a wrong match can suppress or book the wrong company.

## Intended Integrations (not live in this demo)

- **Unipile** (or an equivalent inbox/LinkedIn API) would deliver replies from every connected channel into this skill automatically, instead of a reply being pasted in by hand.
- **A calendar API** (Google Calendar, Cal.com, or similar) would own the booking step in Step 5, proposing live slots, holding the reservation, and confirming back to the lead once one is picked, rather than this skill describing what the booking would contain.
- **Slack** (via webhook) would deliver an alert the moment a reply lands as `negative_hostile`, `unsubscribe`, or `other`, so a human sees the escalation immediately, instead of the flag only surfacing in this skill's run output.
- None of this is wired into the demo repo. This skill runs on a pasted or exported reply and states plainly, at each step, what a live integration would be doing there instead.

## Step 1: Read the Reply and Match It to a Lead

Take the reply as given, pasted text, an exported thread, or a webhook payload. Note the channel it arrived on (email, LinkedIn, WhatsApp), the timestamp, and the full reply text, not just a snippet.

Match the reply to an existing lead record using the same identity rule `system_of_record.md` uses everywhere else in this repo: a stable identifier (domain, or the outreach thread the reply is attached to) beats a fuzzy one (a name match). If no confident match exists, flag it and stop here rather than guessing, a misattributed reply can suppress or book the wrong company.

Pull the lead's dossier (`research.md` output) and the specific outreach touch this reply is responding to, from `outreach-draft-and-send`. Both are required before Step 4 can draft anything grounded.

## Step 2: Classify the Reply

Every reply gets exactly one label:

| Label | What it means |
|---|---|
| `positive_interested` | Clear buying intent, asks for next steps, pricing, or a call. |
| `positive_soft` | Positive in tone, no committed action yet ("interesting, let me think about it"). |
| `positive_referral` | Points to a different contact as the right person, still a live lead, just not this one. |
| `neutral_question` | A genuine clarifying question, neither accepting nor declining. |
| `negative_notnow` | A timing objection, soft no. |
| `negative_notfit` | Doesn't match their need or priorities right now, soft no. |
| `negative_hostile` | Explicitly hostile or demands no further contact, hard no. |
| `unsubscribe` | An explicit opt-out request or unsubscribe action. |
| `ooo` | Automated out-of-office response. |
| `bounce` | Delivery failure, not a human reply at all. |
| `other` | Doesn't cleanly fit any label above. |

`positive_reply_rate = positive_replies / total_sent`, counting `positive_interested`, `positive_soft`, and `positive_referral` as positive. This is a directional health metric for the channel and copy variant that produced the original touch, it feeds `campaign-learning-loop`'s cohort comparisons, it isn't computed or acted on inside this skill.

`ooo` and `bounce` are delivery-layer signals, not a person's opinion of the outreach. Log an `ooo` and resume the normal sequence after any stated return date. Log a `bounce` and flag that specific contact detail as invalid for that channel, without touching the lead's other channels.

If a reply genuinely doesn't fit any label, use `other` and escalate to a human read rather than forcing it into the closest-sounding category. A forced-fit label does more damage than an honest `other`.

## Step 3: Apply the Suppression Check (Hard Negative and Unsubscribe)

This is the one step in this skill with zero discretion.

- **`negative_hostile` or `unsubscribe`, on any channel:** suppress outreach on every channel for this lead, immediately, not just the channel the reply arrived on. Cancel any touch already queued on another channel for this lead. This is the rule `directives/reply_handling.md` states as non-negotiable, and it exists because an earlier version of this system missed exactly this case, see `context/decisions-log.md`, 2026-06-28.
- **`negative_notnow` or `negative_notfit`:** pause the current sequence on this lead. Don't touch other leads, don't set the global suppression flag, and don't block this lead from re-entering the pipeline later under `icp_filtering.md` if a new signal appears.
- **`positive_referral`:** the current lead isn't suppressed or paused, they pointed elsewhere. Flag the referred contact as a new intake candidate for `signal-harvest` / `icp_filtering.md`, carrying the referral source as context, don't silently drop it.

## Step 4: Draft a Grounded Reply

Applies to `positive_interested`, `positive_soft`, `positive_referral`, and `neutral_question`. Every other label skips this step, there's nothing to draft in response to a hard no, an opt-out, an autoresponder, or a bounce.

- Reference the specific signal or claim that started the conversation, not a generic "thanks for getting back to me."
- Answer a `neutral_question` directly using only what the dossier's safe-claims list supports. If the dossier doesn't cover it, say that plainly in the draft rather than inventing an answer.
- For `positive_referral`, draft a short reply to the original contact acknowledging the redirect, and a separate short intake note for the referred contact, not one message trying to do both jobs.
- Queue the draft in the same approval queue `outreach.md` uses for first-touch sends. Nothing here sends on its own.

## Step 5: Carry a Positive Reply to a Booking

If a `positive_interested` reply already proposes or accepts a specific time, or a follow-up exchange after Step 4's approved reply results in the lead agreeing to meet, this is the close state for this stage: carry it to a calendar booking rather than leaving it as "reply logged."

A positive reply that hasn't yet confirmed a time stays in the drafted-and-queued state from Step 4, it isn't a booking until the lead has actually agreed to a slot. Don't count a warm "sure, happy to chat sometime" as booked.

## Step 6: Hand Off to the System of Record

This skill decides what happened to a reply, it doesn't own the write. Every outcome, classified, suppressed, paused, drafted, or booked, hands off to `system-of-record-sync`'s single-writer function with a reason attached (which label fired, which action followed). See `directives/system_of_record.md` for why every field update runs through one writer instead of this skill, or any other, editing a lead record directly.

## Worked Example (fictional)

**Nova Systems Lab, Maya Patel, positive path.**

Maya replies to the LinkedIn DM `outreach-draft-and-send` queued off her dossier (safe claims: three open SDR roles posted in the last two weeks reporting to her, and a LinkedIn post about scaling outbound this quarter): *"This is well timed, we're mid-way through interviewing for those SDR roles right now and honestly the ramp time is what worries me most. Can we find 20 minutes this week?"*

Step 2: explicit interest plus a direct ask for time. Classified `positive_interested`.
Step 3: no suppression, no pause, nothing to do here.
Step 4: drafted reply grounded in the dossier, references the SDR roles and the ramp-time concern she raised, doesn't restate the whole original pitch, proposes two concrete windows. Queued for approval:

```
QUEUE: reply_drafts
Lead: Nova Systems Lab, Maya Patel (Head of Sales)
Label: positive_interested
Status: PENDING_APPROVAL
Draft: "Glad the timing lined up, and ramp time is exactly the piece I focus
on, keeping pipeline moving while the new SDRs get up to speed rather than
everything pausing until they're ramped. Does Wednesday 10am or Thursday
2pm work better for 20 minutes?"
Grounded in: SDR roles (dossier safe claim), Maya's stated ramp-time concern
(this reply)
Next action: awaiting human approval. Nothing sends until that happens.
```

Step 5: the approved reply goes out, Maya confirms Thursday 2pm. Carried to a calendar booking, this lead's stage closes on "booked," not "reply logged."
Step 6: handed off to `system-of-record-sync`: label `positive_interested`, action `booked`, reason logged against the lead record.

**RelayDesk AI, Leah Morgan, hard-negative path.**

Leah replies to an email touch: *"Stop emailing me, take me off whatever list this is."*

Step 2: an explicit demand for no further contact. Classified `negative_hostile`, not `unsubscribe`, there's no opt-out link or keyword, but the intent is unambiguous.
Step 3: suppression fires on every channel for RelayDesk AI, not just email. A LinkedIn follow-up already queued for later that week is cancelled as part of this same action, it never gets the chance to send.
Step 4: skipped, there's nothing to draft in response to a hard no.
Step 6: handed off to `system-of-record-sync`: label `negative_hostile`, action `suppressed (all channels)`, reason logged against the lead record, matching the 2026-06-28 decision this exact scenario is based on.

## Rules

- Classification always comes first. No downstream action fires off raw reply text without a label attached.
- A hard negative or unsubscribe on any channel suppresses every channel for that lead. This is not a per-lead judgment call, apply it every time.
- Soft negatives pause, they don't suppress, and they don't block a later re-entry into the pipeline.
- A drafted reply must trace every claim to the dossier or an offered resource. No generic acknowledgments, no invented specifics.
- Nothing generated by this skill sends itself. Every draft queues for the same human approval gate as first-touch outreach.
- A confirmed positive reply is carried to a booking as the close, not left at "reply logged."
- This skill decides the outcome, it doesn't write the record. Every action hands off to `system-of-record-sync` with a reason attached.
