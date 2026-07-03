"""
Spend gate: Layer 3 execution for spend-and-cost-guard
(see .claude/skills/spend-and-cost-guard/SKILL.md).

Reference/example implementation. Fictional data only (context/example-leads.md).
No live API calls, no credentials.

Adapted from wreynoir/company-enrichment-skill's cheap-check-before-paid-spend
gate: a deterministic ICP match check runs and prints a clear MATCH/NO MATCH
result before any paid enrichment/research step is allowed to run.
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass
class GateResult:
    company: str
    icp_match: bool
    cache_hit: bool
    allowed: bool
    reason: str


def _cache_lookup(company: str, cache: dict, freshness_days: int, age_days: int) -> bool:
    return company in cache and age_days <= freshness_days


def check_spend_gate(
    company: str,
    icp_tier: str,
    cache: dict,
    age_days: int = 0,
    freshness_days: int = 14,
) -> GateResult:
    """
    Mirrors directives/cost_control.md: no paid step runs on a lead that
    hasn't cleared icp-qualify, and no paid step re-runs on a lead whose
    cached result is still fresh.
    """
    icp_match = icp_tier in ("TIER_1", "TIER_2")

    if not icp_match:
        return GateResult(
            company=company,
            icp_match=False,
            cache_hit=False,
            allowed=False,
            reason=f"NO MATCH: {icp_tier} does not clear the spend threshold. "
            "Recommendation: do not spend research/enrichment credits.",
        )

    if _cache_lookup(company, cache, freshness_days, age_days):
        return GateResult(
            company=company,
            icp_match=True,
            cache_hit=True,
            allowed=False,
            reason=f"MATCH, but cached result is {age_days}d old "
            f"(freshness window {freshness_days}d): reuse cache, skip re-spend.",
        )

    return GateResult(
        company=company,
        icp_match=True,
        cache_hit=False,
        allowed=True,
        reason="MATCH: no fresh cache entry. Paid research/enrichment step allowed to run.",
    )


if __name__ == "__main__":
    cache = {"RelayDesk AI": {"researched_at": "2026-06-28"}}  # 5 days before the fixture's fictional "today" of 2026-07-03

    print(check_spend_gate("Nova Systems Lab", "TIER_1", cache))
    print(check_spend_gate("RelayDesk AI", "TIER_2", cache, age_days=5, freshness_days=14))
    print(check_spend_gate("Some Low-Fit Co", "TIER_4", cache))
