"""Shared reference candidate registry safety checks."""

from __future__ import annotations

ALLOWED_CANDIDATE_STATUS = {"candidate_registered", "proposed_internal"}

REQUIRED_BLOCKED_FIELDS = {
    "route_status": "not_route_created",
    "sitemap_status": "not_sitemap_eligible",
    "publication_status": "publication_blocked",
}


def validate_candidates_blocked_only(candidates: list, error) -> bool:
    """Return True if every registry candidate is internal-only and blocked from public output."""
    ok = True
    for entry in candidates:
        if entry.get("public_reference_pilot_status") == "converted_to_controlled_public_reference_pilot":
            continue
        cid = entry.get("candidate_id", "?")
        status = entry.get("candidate_status", "")
        if status not in ALLOWED_CANDIDATE_STATUS:
            error(f"candidate {cid}: invalid candidate_status {status}")
            ok = False
        draft_status = entry.get("draft_status", "")
        if draft_status not in ("not_draft_created", "internal_draft_created"):
            error(f"candidate {cid}: invalid draft_status {draft_status}")
            ok = False
        for field, expected in REQUIRED_BLOCKED_FIELDS.items():
            if entry.get(field) != expected:
                error(f"candidate {cid}: {field} must be {expected}")
                ok = False
        if entry.get("route_active") is True or entry.get("sitemap_eligible") is True:
            error(f"candidate {cid}: must not be route-active or sitemap-eligible")
            ok = False
        if entry.get("draft_created") is True or entry.get("publication_eligible") is True:
            error(f"candidate {cid}: must not be draft-created or publication-eligible")
            ok = False
    return ok
