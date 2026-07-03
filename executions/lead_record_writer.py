"""
Single-writer lead record update: Layer 3 execution for system-of-record-sync
(see .claude/skills/system-of-record-sync/SKILL.md).

Reference/example implementation. Fictional data only (context/example-leads.md).
No live database connection: `RECORDS` is an in-memory stand-in.

The single-writer-with-reason-code pattern here is my own design (no real
external Claude Code skill implementing exactly this was found during
research: see the skill's "Adapted from" note for what WAS found and cited:
TomGranot/hubspot-admin-skills' dedup-by-domain and audit-before-suppress
patterns, which this script's dedupe half draws on directly).
"""
from __future__ import annotations

import json
from datetime import datetime, timezone


RECORDS: dict[str, dict] = {}
AUDIT_LOG: list[dict] = []


def _domain(company: str, website: str) -> str:
    return website.lower().removeprefix("https://").removeprefix("http://").split("/")[0]


def find_existing(website: str) -> str | None:
    """Dedup on domain: the reliable key. Name-string matching has a real
    false-positive rate and is deliberately not used here (see
    directives/system_of_record.md)."""
    target = _domain("", website)
    for company, record in RECORDS.items():
        if _domain(company, record["website"]) == target:
            return company
    return None


def apply_lead_update(company: str, fields: dict, reason: str, caller: str) -> dict:
    """The single write path. No skill in this repo edits RECORDS directly: every update, from every stage, goes through this function."""
    existing = find_existing(fields.get("website", ""))
    if existing and existing != company:
        raise ValueError(
            f"Domain match found for an existing record ({existing}) under a "
            f"different company name ({company}): flag for human merge "
            "decision, do not auto-merge on a fuzzy name match."
        )

    record = RECORDS.setdefault(company, {})
    before = dict(record)
    record.update(fields)

    AUDIT_LOG.append(
        {
            "company": company,
            "caller": caller,
            "reason": reason,
            "before": before,
            "after": dict(record),
            "at": datetime.now(timezone.utc).isoformat(),
        }
    )
    return record


if __name__ == "__main__":
    apply_lead_update(
        "Nova Systems Lab",
        {"website": "https://example.com/nova-systems-lab", "icp_tier": "TIER_1", "research_status": "pending"},
        reason="icp-qualify scored TIER_1, queued for research",
        caller="icp-qualify",
    )
    apply_lead_update(
        "Nova Systems Lab",
        {"research_status": "complete", "dossier_url": "internal://dossiers/nova-systems-lab"},
        reason="signal-research-dossier completed with 2 corroborating signals",
        caller="signal-research-dossier",
    )

    try:
        apply_lead_update(
            "Nova Systems Lab Inc",
            {"website": "https://example.com/nova-systems-lab"},
            reason="duplicate import attempt from a second source batch",
            caller="signal-harvest",
        )
    except ValueError as e:
        print(f"Blocked as designed: {e}")

    print(json.dumps(AUDIT_LOG, indent=2))
