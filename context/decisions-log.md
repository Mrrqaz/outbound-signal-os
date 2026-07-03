# Decisions Log (fictional, seeded)

Fictional decisions showing the skills in this repo in use over time. Dated relative to a fictional "today" of 2026-07-03, for internal consistency across worked examples.

---

**2026-06-20: Research-readiness gate should not re-check leads that already cleared a real qualification decision upstream.**
Status: Closed.
Owner: system design.
Early version of `icp-qualify` re-ran the fit gate on every connected lead before allowing deep research, including leads imported from a pre-vetted list that already carried a real upstream qualification decision. That re-check was redundant at best and miscalibrated at worst: the imported list's own screening process didn't map cleanly onto this system's signal-based fit criteria. Decision: leads carrying a prior real qualification decision (an explicit source marker) skip the gate; the gate exists for leads that only ever received a shallow heuristic check at ingestion. See `directives/icp_filtering.md` and `executions/icp_score.py`.
(This mirrors a real fix I shipped in the production system, generalized here.)

---

**2026-06-24: Learning-loop promotions require a human decision, not an automatic cutover.**
Status: Closed.
Owner: system design.
Considered auto-promoting a winning outreach variant the moment the significance gate cleared. Decided against it: a statistically significant result on a thin cohort can still be a fluke, and swapping the live copy without a human glance removes the one checkpoint that catches "the winning variant only won because of one outlier reply." Promotion stays a one-command human action after the gate clears, not an automatic cutover. See `directives/learning_loop.md`.

---

**2026-06-28: Hostile or unsubscribe replies suppress every channel for that lead, not just the channel it arrived on.**
Status: Closed.
Owner: system design.
A lead who replies "unsubscribe" to an email but hasn't said anything on LinkedIn was still receiving a scheduled LinkedIn follow-up under the first version of `reply-to-pipeline`. Decided that a hard-negative or opt-out signal on any channel suppresses every channel for that lead: the lead doesn't experience the system as five separate channels, they experience it as one company contacting them. See `directives/reply_handling.md`.

---

**2026-07-01: Open: whether `campaign-learning-loop` should track subject-line variants separately from body-copy variants.**
Status: Open.
Owner: system design.
Current version treats each outreach draft as one variant (subject + body together). Splitting them would allow finer-grained learning but roughly doubles the cohort size needed before the significance gate clears on either dimension. Not resolved: flagged for the next review of `directives/learning_loop.md`.
