---
name: spend-and-cost-guard
description: Cross-cutting cost control that sits underneath every paid step in the pipeline (deep research, enrichment, LLM generation at scale), not a pipeline stage of its own. Gates a paid call behind a cheap, deterministic ICP-tier pre-check, checks a cache before re-spending on a lead already processed within its freshness window, rotates across provisioned API keys on a rate-limit or credit ceiling instead of stalling the pipeline, and tracks cumulative spend per lead so cost stays proportional to lead quality instead of uniform across every lead. Run before signal-research-dossier or any paid enrichment step touches a lead, or when asked to check the spend gate, check the cache, or explain why a lead was blocked from a paid call.
user_invocable: true
---

# Spend & Cost Guard

Every stage past `icp-qualify` costs real money: deep research calls, paid enrichment, LLM generation at scale (`directives/cost_control.md`). This is the control that keeps that spend proportional to lead quality instead of uniform across every lead regardless of fit. It's a cross-cutting control sitting underneath the pipeline, not a stage of its own: `signal-research-dossier` and any enrichment step check in here before they spend anything. Four mechanics, in order: a cheap deterministic gate before a paid call, a cache check before a re-spend, key rotation when a provider's limit is hit mid-run, and a running per-lead spend ledger, so "is this system spending proportionally" is a number that can be checked, not a guess.

## Adapted from

Two mechanics below come from real, verified sources. Two don't, and I'd rather say that plainly than invent a citation that reads well.

**The gate (Step 2): wreynoir/company-enrichment-skill** (github.com/wreynoir/company-enrichment-skill, 0 stars, pushed 2026-01-27), file `commands/company-enrichment.md`. Its Phase 1 runs a cheap Tavily search, checks the result against a stored ICP file, and prints a literal `📋 ICP CHECK: ✅ MATCH / ❌ NO MATCH` before Phase 2's paid Apollo/LeadMagic calls are allowed to run; on no-match it prints "Recommendation: Do not spend enrichment credits / Proceed anyway? [y/n]" rather than silently blocking. Step 2 below adapts that same MATCH/NO-MATCH-before-spend structure. This is the same repo cited for the analogous gate inside `waterfall-enrichment` in the sibling GTM repo: the same real mechanic, reused here for a broader cost control rather than for one enrichment step specifically.

**The cache (Step 3): jeremylongshore/claude-code-plugins-plus-skills** (2,469 stars), file `plugins/api-development/api-cache-manager/skills/managing-api-cache/SKILL.md`. This is a real, substantive cache-aside pattern (deterministic cache-key generation from method, path, and params; a per-endpoint TTL policy; tag-based invalidation on mutation; stale-while-revalidate), but it's a generic API-caching skill, not one built for lead enrichment or research. I'm adapting a general-purpose pattern to this specific use case, not porting an enrichment-specific one, and it's worth saying that directly rather than implying a closer fit than exists. Step 3 also deliberately drops the source pattern's stale-while-revalidate behavior; the reasoning is in that step.

**Key rotation (Step 4): no real Claude Code skill found.** I looked. `jeremylongshore/claude-code-plugins-plus-skills` has its own `key-rotation-manager/SKILL.md` (under `skills/04-security-advanced/`), but on inspection it is auto-generated boilerplate with no actual rotation logic; I checked it and rejected it rather than citing something hollow. The one real thing I found was `KarpelesLab/teamclaude` (86 stars), a maintained multi-account Claude proxy that implements genuine quota-based key rotation and 429 handling. It's a documented pattern from a real, working tool, not a Claude Code skill I adapted, so Step 4 below is designed from that pattern, not ported from it.

**Per-lead cumulative spend tracking (Step 5): my own design.** I didn't find this as a real citable mechanic in any Claude Code skill I looked at. `directives/cost_control.md` asks for per-lead spend visibility explicitly ("track cumulative spend per lead across every paid step"), and Step 5 below is built to satisfy that requirement, not adapted from an external source.

## Operating Rules (read first)

- **The gate is a hard stop, not a soft signal.** A TIER_3/TIER_4 lead does not get a paid call "just this once." The entire point of a spend gate is that it actually gates.
- **This skill is a checkpoint, not the doer.** It doesn't run the paid research or enrichment call itself. It decides whether `signal-research-dossier` or an enrichment step is allowed to make that call, and logs what happened once it does.
- **Cache reuse is bounded by the freshness window, never open-ended.** A cache hit inside the window is a legitimate zero-cost result. A cache entry past the window is worth nothing here; it goes through the same gated path as a lead with no cache at all.
- **Key rotation is a capacity fallback, not a policy workaround.** Rotating across provisioned keys to keep a qualified lead's research moving is fine. Rotating to dodge a provider's actual rate limit or terms is not, and this skill doesn't do the latter.
- **Every credit spent, or not spent, gets attributed to a specific lead.** A cost figure with no lead attached can't answer whether spend is proportional to quality; it can only answer whether the month's total looks fine.
- **Say when a mechanic doesn't have a real citable source**, rather than inventing one that reads well. Two of this skill's four mechanics (Step 4's key rotation, Step 5's per-lead ledger) are my own design, not adapted; see Adapted From above.

## Intended Integrations (not live in this demo)

- **A paid enrichment or deep-research provider** (an Apollo/Clay-style firmographic and contact-data API, or an LLM-based deep-research provider behind `signal-research-dossier`) is the actual thing Step 2's gate is protecting spend on. In a live build, this skill's gate result is the precondition check those tools' API calls run behind, not a call this skill makes itself.
- **A keyed cache store** (Redis or similar) would back Step 3 instead of the in-memory dict `executions/spend_gate.py` uses as a stand-in, with a real TTL per paid-step type instead of the single hardcoded freshness window shown here.
- **A secrets manager or API key vault** (AWS Secrets Manager, Doppler, or similar) would hold the provisioned key pool Step 4 rotates across instead of a hardcoded list, and would report real quota/429 state per key rather than this skill inferring it from a provider's response.
- **The CRM/data warehouse write path**, via `system-of-record-sync`'s single-writer pattern, would carry the real `cumulative_spend` field Step 5 updates, instead of the in-memory `RECORDS` dict `lead_record_writer.py` uses as a stand-in.
- **A billing or usage dashboard**, native to each paid provider or a lightweight internal one, would read the Step 5 ledger to answer the cost-per-tier proportionality question `directives/cost_control.md` cares about, instead of that comparison being done by hand against the ledger.

None of these are wired into this repo, and this skill makes no live API calls itself. This is a demonstration of the gating, caching, rotation, and spend-tracking logic. The reference implementation is `executions/spend_gate.py`'s deterministic gate check; everything past that (the actual provider calls, the actual cache store, the actual key vault) is stated, not built.

## Step 1: Load the Lead's ICP Tier and Cache State

Read the lead's `icp_tier` field, set upstream by `icp-qualify` (`executions/icp_score.py`'s TIER_1 through TIER_4 output). This skill does not recompute fit; it reads a tier that was already decided. Also read the cache for this company, keyed by domain and the specific paid step being requested (a research cache and an enrichment cache for the same lead are separate entries), and note its age against the freshness window (14 days by default, set in `executions/spend_gate.py`; `directives/cost_control.md` requires a defined freshness window but leaves the exact number as a policy setting).

If a lead reaches this skill with no `icp_tier` on record at all, that's a process gap, `icp-qualify` should have run first. Flag it and hold the lead rather than inventing a score to let it through.

## Step 2: Run the Spend Gate (hard, before any paid call)

Compare the tier against the spend threshold in `directives/cost_control.md`: TIER_1 and TIER_2 clear the gate, TIER_3 and TIER_4 do not, matching `executions/spend_gate.py`'s `icp_match = icp_tier in ("TIER_1", "TIER_2")` check exactly.

- **MATCH (TIER_1 or TIER_2):** proceed to Step 3.
- **NO-MATCH (TIER_3 or TIER_4):** stop here. Print the gate result plainly (mirroring the source pattern's `📋 ICP CHECK: ❌ NO MATCH` output), log the lead as blocked with the reason, and do not touch Step 3, Step 4, or any paid provider for it. TIER_3 is a nurture tier upstream in `icp-qualify`, not a disqualification, but it still doesn't clear this spend threshold: a lead worth nurturing isn't automatically a lead worth spending research credits on today.

This is a hard gate, not a recommendation. No "run it anyway to be safe" path exists here, because the entire discipline `cost_control.md` asks for depends on the gate actually holding.

## Step 3: Check the Cache Before Allowing a Fresh Spend

For a lead that cleared Step 2, check whether a cached result already exists for this company and this specific paid step.

- **Fresh cache hit** (age within the freshness window): skip the paid call entirely, reuse the cached result, and log the skip as a zero-cost cache hit, not as if the step never ran.
- **No cache entry, or the cache has aged past its freshness window:** proceed to Step 4; a fresh paid call is allowed.
- **The lead's signal set has materially changed since the cache was written** (a new corroborating signal, a changed job posting, per `directives/cost_control.md`): treat this as an invalidation regardless of age. A real change to the underlying evidence beats a clock that hasn't run out yet.

One deliberate difference from the general-purpose caching pattern this is adapted from: no stale-while-revalidate. The source pattern would serve a stale entry immediately while quietly refreshing it in the background. This skill doesn't do that: an aged research dossier or enrichment record silently served as current could produce an inaccurate outreach angle, so an aged cache entry is treated as a hard miss and goes through the full gated, spend-visible path in Step 4, never a quiet background refresh.

## Step 4: Rotate Keys on Rate-Limit or Exhaustion, Never Bypass

Once a paid call is actually allowed to run (Step 2 MATCH, Step 3 fresh miss), it uses the next available provisioned key for that provider. If the provider returns a rate-limit response, or reports the key has hit its credit ceiling mid-call, rotate to the next provisioned key in the pool and retry, logging the rotation event against the lead.

Rotation is a capacity fallback, not a way around a provider's terms. If every provisioned key for that provider is exhausted, the pipeline does not keep rotating in a loop looking for a workaround: it stops, and either waits for capacity to free up or flags the lead for a human decision. A stalled pipeline is a visible, honest state. A pipeline that quietly works around a provider's rate limit is not.

## Step 5: Log Spend and Update the Per-Lead Ledger

Every attempt from Step 4 (hit, miss, or rotation event) gets logged against the lead with its cost, through the same single-writer pattern the rest of this system uses for record updates (`system-of-record-sync`'s `executions/lead_record_writer.py`: one write path, always a reason). No skill in this repo edits a spend field directly.

Roll individual attempts up into a running `cumulative_spend` total per lead. This is what turns "is this system within budget this month" (a weak question: a system can be within budget and still spend evenly across bad and good leads) into "is this system spending proportionally to lead quality" (the question `cost_control.md` actually cares about), by making it possible to compare cumulative spend against `icp_tier` across a batch and catch a TIER_3/4 lead that slipped past Step 2, or a TIER_1 lead absorbing far more spend than its research actually needed.

## Worked Example (fictional)

Three leads, run through the gate in order, mirroring `executions/spend_gate.py`'s own `__main__` fixtures:

**Nova Systems Lab, TIER_1, no cache entry.**
Step 1: tier `TIER_1` (matches `icp_score.py`'s worked example, total score 88, consistent with the 88% fit score in `context/example-leads.md`), no cached research on file. Step 2: `TIER_1` clears the threshold, MATCH. Step 3: no cache entry, fresh miss, proceed. Step 4: the research call runs; the first provisioned key returns a rate-limit response partway through, rotates to the second provisioned key, call completes. Step 5: logged as `provider: [research provider], result: hit, rotation: 1, cost: 1 unit`, `cumulative_spend: 1 unit`.

**RelayDesk AI, TIER_2, cached 5 days ago.**
Step 1: tier `TIER_2`, cache entry on file dated 5 days old against a 14-day freshness window. This research ran before the later `signal-harvest` re-scan that found the original listing had gone stale (see that skill's worked example), and before Leah Morgan's hostile reply later suppresses the lead entirely (see `reply-to-pipeline`'s worked example); the three worked examples are snapshots of the same fictional lead at different points, not a single contradiction. Step 2: `TIER_2` clears the threshold, MATCH. Step 3: cache is fresh (5 <= 14), cache hit, paid call skipped. Step 5: logged as `result: cache_hit, cost: 0`, `cumulative_spend` unchanged.

**Some Low-Fit Co, TIER_4.**
Step 1: tier `TIER_4`. Step 2: `TIER_4` does not clear the threshold, NO-MATCH. The gate prints the blocked disposition and the pipeline stops there; Steps 3 and 4 never run, and no provider is ever called. Step 5: logged as `result: blocked_pre_spend, cost: 0`.

Across this batch: one unit spent total, on the one TIER_1 lead that actually needed a fresh call. The TIER_2 lead cost nothing because its research was still current. The TIER_4 lead cost nothing because it never should have been spent on in the first place, which is exactly the proportionality `cost_control.md` is asking for.

## Rules

- The Step 2 gate is a hard stop on TIER_3/TIER_4 leads. No "run it anyway" path, no exceptions.
- Never call more than the next provisioned key on a rate-limit. If the whole pool for a provider is exhausted, stop and flag for a human decision; don't invent a workaround.
- A cache hit inside the freshness window skips the paid call entirely. A cache entry aged past the window, or invalidated by a material signal change, is a hard miss, not a stale-while-revalidate serve.
- Every attempt (hit, miss, cache hit, or blocked gate) gets logged with its cost against the lead. A miss still cost a credit in most provider pricing models; log it as a miss, not silently.
- Spend updates go through the single-writer pattern only (`lead_record_writer.py`), never an ad-hoc field edit from inside this skill.
- If a lead has no `icp_tier` on record, flag the gap back to `icp-qualify` rather than guessing a tier to let it through.
