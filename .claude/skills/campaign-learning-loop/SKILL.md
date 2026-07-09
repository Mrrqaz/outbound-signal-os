---
name: campaign-learning-loop
description: Compares outreach variants drafted and sent by outreach-draft-and-send, gates promotion behind a pre-declared significance threshold plus a mandatory human decision, and writes the reusable pattern (not just the win or loss) to a persistent learnings log so future drafting doesn't re-discover the same insight. Run when a running variant test reaches a review point, or when asked "check the test," "can we promote the winner," or "what has this system already learned."
user_invocable: true
---

# Campaign Learning Loop

Outreach copy that never gets tested never improves past a guess, and a test that gets called early off a lucky week is worse than no test at all, it launders noise into false confidence. This skill runs the comparison side of the loop `outreach-draft-and-send` feeds into: it checks whether a running variant test has actually cleared a real significance bar, screens the result against guardrail metrics before treating a headline number as good news, and then stops, on purpose, in front of a human, before anything gets promoted to the live default. Every completed test, win or loss, writes a short entry to a persistent learnings log so the next drafting cycle reads what has already been learned instead of re-running the same question.

**Adapted from:** coreyhaines31/marketingskills, `skills/ab-testing/SKILL.md` (github.com/coreyhaines31/marketingskills). The Statistical Rigor rule (pre-determine sample size, don't peek and stop early, commit to the methodology), the sample-size lookup approach, the guardrail-metric check, and the Experiment Playbook's `Result:` / `Pattern:` logging fields are that skill's design. The instinct to distill a completed test into a reusable pattern instead of a raw win/loss record is also the core mechanic of two smaller repos: haddock-development/claude-reflect-system (confidence-scored correction detection that patches a skill file once, "correct once, never again") and UniM0cha/claude-self-improving-skills (Stop-hook-triggered distillation into SKILL.md, built specifically to avoid redundant relearning). This version implements `directives/learning_loop.md`'s statistical-rigor rule, its human-promotion gate, and its persisted-pattern requirement.

## Operating Rules (read first)

- **Pre-declare the metric and the minimum sample before a test starts.** Don't retrofit "this looks like enough data" once a result already looks good, that is exactly how noise gets mistaken for a real result.
- **Never call a result off a raw percentage on a thin cohort.** A significance gate exists for a reason, hold it even when the early read looks great, especially when the early read looks great.
- **Clearing the significance gate makes a variant eligible, never promoted.** Promotion is a human decision every time, no matter how clean the number, per the 2026-06-24 decision in `context/decisions-log.md`.
- **One variable at a time.** A test that changes the subject line and the body copy together can't tell you which one moved the number. Flag anything else as attribution-weak instead of reporting it as clean.
- **Subject-line and body-copy variants stay combined until the open question resolves.** See the 2026-07-01 open entry in `context/decisions-log.md`, splitting them would roughly double the cohort size needed per dimension, and that tradeoff has not been decided on purpose yet.
- **A test is not done at the promotion decision, it is done when the Pattern field is written.** A win with no captured pattern is a wasted test, the next drafting cycle has nothing to read.
- **This skill does not draft outreach copy or classify replies.** `outreach.md` (via `outreach-draft-and-send`) owns generation, `reply_handling.md` owns what happens to a reply. This skill only compares what has already gone out.

## Intended Integrations (not live in this demo)

- **An experimentation platform** (GrowthBook, or an equivalent open-source significance-testing service) would own the actual sequential significance testing and guardrail-metric alerting in Steps 2 and 3, instead of this skill reasoning through a lookup table by hand.
- **scipy.stats / statsmodels** would run the real two-proportion significance test behind a "cleared the gate" call, rather than the directional read this skill produces from raw counts.
- **The send platforms** (SmartLead for email, HeyReach/Unipile for LinkedIn, Twilio for SMS/voice, or whatever `outreach-draft-and-send` is wired to) would be the live source of per-variant reply counts, instead of a pasted or manually pulled batch.
- **A shared learnings log** (a NocoDB base, mirroring the persistence pattern in claude-reflect-system and claude-self-improving-skills) would hold every test's Pattern field as a queryable table, instead of the flat `context/learnings-log.md` file this skill appends to here.
- None of these are wired into this repo. This demo runs on whatever batch of send results is pasted or exported, and states plainly when a step depends on an integration it does not have.

## Step 1: Pull the Variant Set and Confirm the Test Design

Read the batch of drafts and results `outreach-draft-and-send` has produced for this test: which leads got Variant A vs. Variant B, what differs between them, and what was held constant.

Check the one-variable rule from `directives/learning_loop.md` before anything else. If more than one thing changed between variants (subject line and opener and CTA, all at once), the test cannot attribute a result to any single change, flag it as attribution-weak rather than reporting it as clean. Per the 2026-07-01 open decision, a draft's subject line and body are currently tracked as one combined variant, so don't split them into separate tests, doing that silently would change the cohort math without anyone deciding the tradeoff on purpose.

## Step 2: Check the Significance Gate

Pull the historical baseline reply rate for this segment or signal type from prior sends. If there is no direct history for this exact segment, use the closest comparable segment and say so explicitly, don't invent a baseline.

Minimum sample per variant depends on the lift being claimed, bigger claimed lifts need less data to detect:

| Expected lift (relative) | Approx. minimum sample per variant* |
|---|---|
| 2x (100% relative lift) | ~100-150 |
| 50% relative lift | ~300-500 |
| 20% relative lift | ~1,000-1,500 |

*Rough figures assuming a baseline reply rate in the low single digits. Recompute directionally against the segment's actual baseline rather than treating this table as fixed.

If the actual sample per variant has not reached the pre-declared minimum, the gate has not cleared, full stop. A favorable-looking raw percentage on a handful of sends is not a result, it's a coin flip that has not finished flipping. Report it as inconclusive or still running, not as a lead-in to promotion.

## Step 3: Score Guardrail Metrics

A reply-rate win that arrived alongside a spike in unsubscribes, spam complaints, or hostile replies is not a clean win. Check whether the headline metric moved at the cost of something nobody pre-declared as the target.

Run the guardrail check regardless of whether the significance gate has cleared. A guardrail breach on an early, underpowered read is still worth flagging, it just cannot kill a test that has not reached its minimum sample yet, it only informs the human review in Step 4.

## Step 4: Route to the Human Promotion Decision

Clearing the significance gate makes a variant eligible for promotion. It does not promote it. This is deliberate, not a workflow gap. Per the 2026-06-24 decision in `context/decisions-log.md`, an early version of this system considered auto-promoting the moment the gate cleared and rejected it: a statistically significant result on a thin cohort can still be a fluke, and cutting over without a human glance removes the one checkpoint that catches "this only won because of one outlier reply."

Present the human reviewer with the pre-declared success/failure criteria, the actual result, the guardrail check from Step 3, and one explicit question, does this pattern look real enough to become the new default. The reviewer's job is not to re-run the math, it is to sanity-check what the math cannot see: an outlier reply skewing a small cohort, a variant that happens to have landed on a better-fit sub-segment by chance, or copy that reads as a template with a variable dropped in rather than a real message.

Promotion is a single explicit action after that review, not an automatic cutover. If the reviewer declines to promote a variant that cleared the gate, log why, that reasoning is itself a pattern worth keeping.

## Step 5: Persist the Pattern, Not Just the Win or Loss

Every completed test, whether it ends in promotion, rejection, or inconclusive, writes a short entry to the persistent learnings log (`context/learnings-log.md`, created on first entry the same way `context/decisions-log.md` is append-only and dated).

The entry needs a `Result:` field and a `Pattern:` field, and the Pattern field is the one that matters most. Result records what happened this time. Pattern records what a future test-design pass should already know before proposing a new hypothesis, so the system does not spend another cohort rediscovering it.

```
Test: [name]
Segment/signal type: [...]
Variants: [A description] vs [B description]
Baseline rate used: [X%, source]
Pre-declared minimum sample per variant: [N]
Actual sample reached: A=[n], B=[n]
Actual result: A=[rate], B=[rate]
Guardrail check: [clean | flagged, reason]
Verdict: [Promoted | Rejected | Inconclusive]
Human reviewer decision: [one line, what decided it and why]
Result: [winner/loser/inconclusive] - [metric] changed by [X%]
Pattern: [the reusable insight, written so a future test-design pass can read it without re-deriving it]
```

## Worked Example (fictional)

A test runs against the hiring-signal segment, leads with a public "hiring SDR/growth" job posting, the same signal every lead in `context/example-leads.md` was sourced on. Two openers for the same outreach sequence, subject line and CTA held constant per the one-variable rule:

- **Variant A** (generic signal-mention opener): "Saw you're hiring for [role], wanted to reach out..."
- **Variant B** (role-plus-consequence opener): "Saw the [role] req. Teams usually post that one when pipeline coverage is already behind, not before..."

**Step 1, design check:** one variable only, the opening line. Subject and CTA are identical across A and B. Per the 2026-07-01 open decision, this test does not attempt to split subject-line performance from body-copy performance.

**Step 2, Day 3 checkpoint:** the six leads in `context/example-leads.md` are this test's earliest slice. Variant A went to QueryForge Cloud, StackPilot Software, and BeaconDesk SaaS, 0 replies from 3 sends. Variant B went to Nova Systems Lab, RelayDesk AI, and OpsLayer CRM, 1 reply (Maya Patel at Nova Systems Lab). Raw read: 0% vs. 33%. Baseline reply rate for this signal type, from the closest comparable segment, runs about 8%. Detecting even a 2x lift needs roughly 100-150 sends per variant, at n=3 per variant the gate is nowhere close to clearing. Report this as **inconclusive, still running**, not as an early win, one reply on three sends is not a 33% reply rate, it's a single data point wearing a percentage sign.

**Step 3, guardrail check at Day 3:** no unsubscribes, no hostile replies, no complaints on either variant. Nothing to flag, but this does not offset the sample-size gap from Step 2.

**Step 4, full window, four weeks later:** the same variant pair kept running against the full qualified hiring-signal segment beyond the six-lead fixture. Final counts: Variant A reached 128 sends at 9 replies (7.0%). Variant B reached 131 sends at 19 replies (14.5%), a 2.07x lift, clearing the pre-declared 2x/120-sample gate. Guardrail check stays clean, no unsubscribe or complaint spike on either variant.

The gate cleared, so Variant B is eligible. Per the 2026-06-24 rule, eligible is not promoted. Human review checks whether the 19 replies on Variant B cluster around one unusually receptive account (they don't, replies spread across 14 different companies) and confirms the opener reads naturally rather than as a template with a variable dropped in. The reviewer promotes Variant B to the default opener for this signal type.

**Step 5, logged entry:**

```
Test: Role-plus-consequence opener vs. generic signal-mention opener
Segment/signal type: hiring-signal leads (SDR/growth-role postings)
Variants: A) generic signal-mention opener  B) role-plus-consequence opener
Baseline rate used: 8%, estimated from closest comparable signal-type segment
Pre-declared minimum sample per variant: 120 (2x-lift target)
Actual sample reached: A=128, B=131
Actual result: A=7.0%, B=14.5%
Guardrail check: clean, no unsubscribe/complaint spike, replies spread across 14 accounts
Verdict: Promoted
Human reviewer decision: promoted Variant B, replies not concentrated in one account, opener reads naturally
Result: winner - reply rate changed by +107% (14.5% vs. 7.0%, 2.07x)
Pattern: naming the specific role plus the operational consequence of that hiring signal ("this role gets posted when X is already true") outperforms a plain signal-mention opener on hiring-signal leads. Try this framing first on future hiring-signal segments before re-testing generic vs. specific from scratch.
```

That Pattern line is what the next test-design pass should read before proposing a new hypothesis on a hiring-signal segment. The generic-vs-specific opener question is now answered for this signal type, a new test here starts one step further along, not from scratch.

## Rules

- Never promote a variant on a raw percentage that has not reached the pre-declared minimum sample. A result on three sends is not a result.
- Clearing the significance gate makes a variant eligible for promotion, never promoted. Promotion is a human decision, every time, per the 2026-06-24 rule in `context/decisions-log.md`.
- Never call a test clean when more than one variable changed. Flag combined changes as attribution-weak.
- Don't split subject-line and body-copy into separate variants until the open 2026-07-01 decision resolves that question. Treat each draft as one combined variant until then.
- A guardrail breach, unsubscribes, complaints, hostile replies, gets flagged regardless of whether the significance gate has cleared.
- Every completed test writes a Pattern field to the learnings log, not just a Result. A test that ends without a captured pattern gains the next cycle nothing.
- If a reviewer declines to promote a variant that cleared the gate, log the reasoning as its own pattern, that's still useful information for next time.
