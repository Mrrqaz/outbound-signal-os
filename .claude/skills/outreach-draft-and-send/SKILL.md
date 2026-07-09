---
name: outreach-draft-and-send
description: Turn a completed research dossier into personalized outreach drafts across the channels that actually fit the lead (LinkedIn and email as primary; WhatsApp, SMS/voice, and meme follow-ups as gated later touches), run every draft through a verified-claims QA gate, and hold everything in an approval queue. Nothing drafted here sends itself. Run once a dossier clears `signal-research-dossier`, or when asked to "draft outreach for [lead]," "stage the sequence," "what's in the approval queue," or "queue this for send."
user_invocable: true
---

# Outreach Draft & Send

Adapted from growthenginenowoslawski's `coldoutboundskills` repo (github.com/growthenginenowoslawski/coldoutboundskills, 475 stars, 174 forks), `skills/smartlead-campaign-upload-public/SKILL.md`, whose never-auto-launch mechanic is the design behind the approval gate below: campaigns are always created in draft, reviewed in the Smartlead UI, and started manually, and "Cold email launches should never happen from a script." That skill is email-only and delegates content generation to companion skills in the same repo (`campaign-copywriting`, `personalization-subagent-pattern`). The QA gate in Step 4 is adapted from gtmagents' `gtm-agents` repo (github.com/gtmagents/gtm-agents, 303 stars, 50 forks), `plugins/copywriting/skills/cold-email-personalization/SKILL.md`, which requires "at least 2 verified signals per prospect," states "never fabricate facts," and gates drafts behind an 80/100 QA scoring rubric before send. The instinct to hold a full multi-touch sequence for human review in one place borrows from amplemarket's `skills` repo (github.com/amplemarket/skills), `torpedo/SKILL.md` Phase 3, which builds email+LinkedIn sequences and states to "present the full sequence for the user to review before they activate it." I did not find a real external skill that runs a true multi-channel approval queue (LinkedIn, email, WhatsApp, SMS/voice, and meme follow-ups) in one place. That combination is my own synthesis on top of these single- and dual-channel gate patterns, not directly sourced, and I am stating that plainly rather than implying otherwise.

A drafted message that invents a claim, or a send that skips human review, does more damage to a pipeline than a weak subject line ever could. This skill exists to turn a completed dossier into outreach that's actually earned: grounded only in what research verified, staged only across the channels this lead genuinely supports, and held in a queue until a person says go.

## Operating Rules (read first)

- **Every claim in a draft must trace to the dossier's safe-claims list** (`research.md`). Never assert something the dossier only implied, and never draft from the avoid-claims side even when it would read as a sharper pitch.
- **Not every lead gets every channel.** Draft only the channel(s) the dossier's route recommendation and the lead's actual public presence support: offering a resource, a LinkedIn touch, an email, or a WhatsApp message only where the evidence and reachability make it a real fit, not a default.
- **WhatsApp, SMS/voice, and meme follow-ups are later-touch channels, never a first touch.** They're used sparingly, only once a prior touch has established some relationship or the dossier explicitly notes context that makes them appropriate. A meme is a follow-up nudge on a lead that's already been contacted, matched to that lead's actual signal, not a cold opener and not decoration.
- **Each touch in a sequence adds new value.** A follow-up that just repeats the first message with different framing ("bumping this") is not a real follow-up, and doesn't belong in the queue.
- **The approval gate is non-negotiable.** Every send requires explicit human approval before it happens, regardless of how confident the ICP score or the research stage was upstream. This skill drafts, QA-checks, and queues. It never sends.
- **A dossier missing a safe-claims list is a blocking gap, not something to draft around.** Hold the lead and say why, rather than drafting from the raw signal summary alone.

## Intended Integrations (not live in this demo)

- **Unipile and HeyReach** would power the LinkedIn channel together once a draft is approved: **Unipile** as the API layer that sends the individual message and reads the reply thread back in for `reply-to-pipeline`, and **HeyReach** as the campaign runner that sequences and paces multi-step LinkedIn touches at account-safe limits. Unipile is the connection; HeyReach is the campaign around it.
- **SmartLead** (or an equivalent email sending platform) would power email sequence delivery and open/click tracking, matching the "always draft, review in the UI, hit start manually" pattern this skill's approval gate is adapted from.
- **A WhatsApp Business API provider** would power WhatsApp delivery on the leads where that channel actually applies.
- **Twilio** would power the SMS and voice follow-up channels, the programmable-messaging and voice API behind a text nudge or a callback on a lead that's already been contacted, never a cold first touch.
- **Supermeme.ai** would generate the personalized meme used in a meme follow-up, a signal-matched image tied to what research actually found on the lead, drafted and queued like every other channel and held for approval before it sends.
- **Slack (via webhook or app)** would deliver the approval queue itself, an actual person approving or rejecting each draft with one click, instead of the structured queue record shown in the worked example below.
- None of these are wired into this repo. Right now this skill produces a drafted, QA-checked, queued record and stops there. Every step past "held for approval" is stated, not executed.

## Step 1: Pull the Dossier and Confirm It's Send-Ready

Read the dossier produced by `signal-research-dossier`: signal summary, why-now angle, proof URLs, the safe-claims-vs-avoid-claims list, and the route recommendation. If the safe-claims list is missing or empty, stop here. Per `research.md`'s anti-fabrication rule, this is a blocking gap, not something to draft around. Flag the lead and hold it rather than drafting from the signal summary alone. Note the route recommendation's stated channel(s) verbatim; that's the input to Step 2, not a suggestion to freelance from.

## Step 2: Decide Which Channels This Lead Actually Gets

Not every lead gets every channel (`directives/outreach.md`). Work through this in order, and only draft what clears it:

1. Start from the dossier's route recommendation for stated channel(s); that's the baseline, not optional context.
2. LinkedIn and email are the default primary channels wherever the lead has a matching public presence (a real LinkedIn profile URL on file for LinkedIn, a verified or clearly plausible work email for email).
3. WhatsApp, SMS/voice (Twilio), and a meme follow-up (Supermeme.ai) are later-touch channels only. They apply if this isn't the first touch, or the dossier explicitly notes context that makes one appropriate. Skip all three by default on a cold open. A meme in particular is a warm-lead nudge tied to the lead's own signal, so it only clears once a prior touch exists and the dossier gives it a specific hook to land on.
4. A resource offer gets bundled onto a channel only when the dossier's evidence genuinely supports it being useful to this specific lead. Skip it when it would read as generic homework, especially on a first touch.

If the route recommendation and the lead's actual reachability disagree (the route says email but no verified email is on file), draft only what's actually reachable and note the gap rather than drafting into a channel that doesn't exist yet.

## Step 3: Draft Each Cleared Channel

Write from the safe-claims list only. Match tone and length to the channel: LinkedIn stays short and conversational; email can carry a subject line and slightly more context; WhatsApp, on the rare lead where it applies, stays shortest and most casual. If this is one touch in a planned sequence, it has to add something the prior touch didn't (a new proof point, a resource, a different angle) rather than restate the same why-now angle with new wording.

## Step 4: QA Gate Before Anything Enters the Queue

A draft only advances if all of the following hold:

- **At least 2 verified claims** from the dossier's safe-claims list appear in the draft, adapted from the gtm-agents 80/100 rubric but simplified here to a hard floor. If the dossier only supports one safe claim, that's a signal the dossier itself is thin (`research.md`): hold the lead rather than pad the draft to hit the count.
- **Zero claims outside the safe-claims list.** No statistic, connection, or inference appears in the draft that isn't explicitly in that list.
- **Personalization is specific, not decorative.** It has to reference something research actually found, not a generic compliment that could apply to any company.
- **Channel and tone match what Step 2 decided.** No channel drift mid-draft, no WhatsApp casualness leaking into the email.

Anything that fails gets revised. If it can't be fixed without fabricating a claim to fill the gap, the draft is held and the reason is stated plainly, not quietly patched over.

## Step 5: Enter the Approval Queue (Hold, Never Send)

Every draft that clears Step 4 is logged into the queue as `PENDING_APPROVAL` with the lead, the channel(s), the draft text, which safe claims it used, and the QA result. This is the non-negotiable gate from `directives/outreach.md`: regardless of ICP score or research confidence, nothing sends without an explicit human approval action against this specific draft. State plainly in the output that the draft is held, not sent.

## Step 6: Handoff

This skill's job ends the moment a draft is queued, and later, approved and sent by a human. Once that send happens, whatever the lead sends back is not this skill's problem to solve. That's `reply-to-pipeline`'s job, which reads the reply thread and classifies and routes it.

## Worked Example (Nova Systems Lab, fictional)

**Dossier in (from `signal-research-dossier`):** Nova Systems Lab, contact Maya Patel, Head of Sales, ICP fit 88%. Signal summary: three SDR roles posted on Nova's careers page in the last two weeks, all reporting to Maya. Corroborating evidence: a LinkedIn post from Maya ten days ago about "doubling our outbound motion this quarter." Why-now angle: Nova is actively building a new SDR team under Maya right now, a narrow window before those hires are ramped and the outbound process is already locked in. Safe claims: "three open SDR roles posted in the last two weeks, reporting to the Head of Sales" (job board, verifiable) and "Maya posted publicly about scaling outbound this quarter" (LinkedIn, verifiable). Avoid claims: anything implying Nova has no outbound system today, or is struggling; that's inferred, not verified. Route recommendation: LinkedIn primary (Maya has an active public LinkedIn presence), email secondary (verified work email on file).

**Step 2 (channels):** LinkedIn clears (active profile, route recommends it). Email clears (verified address on file, route recommends it). WhatsApp skipped: first touch, no prior relationship, and the dossier states no context for it. Resource offer skipped on this touch too: a full asset on a cold open would read as homework, so it's reserved for touch 2 if Maya engages.

**Step 3 (drafts):**

LinkedIn DM: *"Hi Maya, noticed the three SDR roles you've got open right now, plus your post last week about scaling outbound this quarter. Building out a new team while pipeline still needs to move is a specific kind of hard. I build signal-based outbound systems that keep pipeline moving while new hires ramp, then hand over cleanly once they're up to speed. Worth a quick look at how that'd fit alongside what you're building?"*

Email, subject "Nova's new SDR team + pipeline in the meantime": *"Hi Maya, I saw Nova has three SDR roles open right now, all reporting into you, and your post last week about scaling outbound this quarter. Ramping three new hires takes time even after they start, and pipeline usually still needs to move in that gap. I build signal-based outbound systems that source, qualify, and stage outreach against real buying signals like this one, so pipeline keeps moving while the new team ramps, and hands over cleanly to them once it does. Worth 15 minutes to see if the timing fits?"*

**Step 4 (QA):** 2 verified claims used in each draft (SDR roles, LinkedIn post), both from the safe-claims list. Nothing implying Nova lacks a system today. Personalization is specific to Maya and this week, not generic. Channel/tone match: LinkedIn short, email carries the subject line and slightly more context. WhatsApp correctly absent. Resource correctly held back. **Passes.**

**Step 5 (queue):**

```
QUEUE: outreach_drafts
Lead: Nova Systems Lab, Maya Patel (Head of Sales)
Status: PENDING_APPROVAL
Channels: LinkedIn DM, Email
Safe claims used: 3 open SDR roles (careers page, verified); LinkedIn post on scaling outbound (verified)
QA: 2/2 verified claims, 0 fabricated, channel/tone match confirmed
WhatsApp / SMS-voice (Twilio) / meme (Supermeme.ai): not drafted (all later-touch channels; this is a cold first touch)
Resource offer: not included (reserved for a positive reply, not touch 1)
Next action: awaiting human approval. Nothing sends until that happens.
```

**Step 6 (handoff):** If a human approves both and Maya replies to either one, that reply is `reply-to-pipeline`'s job, not this skill's. This skill's record of Nova Systems Lab stops at "queued and awaiting approval."

## Rules

- Every claim traces to the dossier's safe-claims list. Never draft from an avoid-claim, even when it would read stronger.
- Not every lead gets every channel: draft only what the route recommendation and the lead's real reachability support.
- WhatsApp, SMS/voice (Twilio), and meme follow-ups (Supermeme.ai) are later-touch channels only, never a cold first touch, and a meme has to be matched to the lead's real signal, not used as decoration.
- Each touch in a sequence adds new value. A reworded bump doesn't belong in the queue.
- A draft only enters the queue after the QA gate: 2+ verified claims, zero fabricated claims, confirmed channel/tone match.
- The approval gate is non-negotiable. Nothing drafted here sends itself, no matter how confident the upstream scoring or research was.
- A dossier missing a safe-claims list is a blocking gap. Hold the lead and say so, don't draft from the raw signal alone.
- Once a draft is approved and sent, this skill's job is done. Replies route to `reply-to-pipeline`.
