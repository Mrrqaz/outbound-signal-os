"""
ICP scoring: Layer 3 execution for icp-qualify (see .claude/skills/icp-qualify/SKILL.md).

Reference/example implementation. Fictional data only (context/example-leads.md).
No live API calls, no credentials, no real Autoage scoring internals.

Adapted from janskuba/outbound-agents' lead-prioritizer.md 100-point weighted
formula (see the icp-qualify skill for the full citation).
"""
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class LeadInputs:
    company: str
    # Fit (0-40)
    industry_relevance: int  # 0-15
    company_size_fit: int  # 0-15
    tech_stack_alignment: int  # 0-10
    # Signal strength (0-35)
    signal_recency_specificity: int  # 0-15
    signal_count_diversity: int  # 0-10
    signal_rating: int  # 0-10 (HIGH/MED/LOW mapped upstream)
    # Engagement (0-25)
    linkedin_activity: int  # 0-10
    content_engagement: int  # 0-8
    approachability: int  # 0-7
    missing_categories: list = field(default_factory=list)  # e.g. ["engagement"]


TIER_THRESHOLDS = (
    ("TIER_1", 80, "work today"),
    ("TIER_2", 60, "work this week"),
    ("TIER_3", 40, "nurture"),
    ("TIER_4", 0, "deprioritize"),
)


def score_lead(inputs: LeadInputs) -> dict:
    fit = inputs.industry_relevance + inputs.company_size_fit + inputs.tech_stack_alignment
    signal = inputs.signal_recency_specificity + inputs.signal_count_diversity + inputs.signal_rating
    engagement = inputs.linkedin_activity + inputs.content_engagement + inputs.approachability

    category_scores = {"fit": fit, "signal": signal, "engagement": engagement}
    category_max = {"fit": 40, "signal": 35, "engagement": 25}

    # Missing-data rule (directives/icp_filtering.md): a category flagged as
    # missing evidence is capped at 50% of its max. Two cases:
    # - no evidence at all: score the cap itself, never a true zero (a lead
    #   nobody could evaluate must not look identical to one evaluated and bad);
    # - partial evidence: the cap is a ceiling, not a floor. An honest low
    #   partial read stays low; a partial read that would rival a fully
    #   verified score gets pulled down to the cap.
    for category in inputs.missing_categories:
        cap = category_max[category] // 2
        raw = category_scores[category]
        category_scores[category] = cap if raw == 0 else min(raw, cap)

    total = sum(category_scores.values())

    tier, _, action = next(t for t in TIER_THRESHOLDS if total >= t[1])

    return {
        "company": inputs.company,
        "category_scores": category_scores,
        "total": total,
        "tier": tier,
        "action": action,
        "partial_evaluation": bool(inputs.missing_categories),
    }


if __name__ == "__main__":
    # Nova Systems Lab: hero lead, context/example-leads.md. Fully evaluated,
    # no missing categories.
    nova = LeadInputs(
        company="Nova Systems Lab",
        industry_relevance=15,
        company_size_fit=12,
        tech_stack_alignment=8,
        signal_recency_specificity=15,
        signal_count_diversity=8,
        signal_rating=10,
        linkedin_activity=8,
        content_engagement=6,
        approachability=6,
    )
    print(score_lead(nova))

    # QueryForge Cloud: supporting batch. LinkedIn activity and content
    # engagement have real evidence, but approachability is truly unverified
    # (no open contact path found), so the engagement category is flagged
    # missing and its raw 15 gets pulled down to the 12-point cap. Matches the
    # icp-qualify skill's worked example: 32 + 26 + 12 = 70, TIER_2.
    queryforge = LeadInputs(
        company="QueryForge Cloud",
        industry_relevance=13,
        company_size_fit=13,
        tech_stack_alignment=6,
        signal_recency_specificity=13,
        signal_count_diversity=5,
        signal_rating=8,
        linkedin_activity=10,
        content_engagement=5,
        approachability=0,
        missing_categories=["engagement"],
    )
    print(score_lead(queryforge))
