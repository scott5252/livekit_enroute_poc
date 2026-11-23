"""Work out what is missing from a visit, in code.

The briefing must state data gaps plainly. Deciding what counts as a gap is a
rule, so it lives here where it can be unit tested, and the language model is
simply told what to say.
"""

from __future__ import annotations

from .models import Visit

# Care Manager text fields worth calling out when they are empty.
_CARE_MANAGER_FIELDS = {
    "precautions": "precautions",
    "home_access": "home access details",
    "nursing_instructions": "nursing instructions",
    "featured_note": "featured note",
}


def find_data_gaps(visit: Visit) -> list[str]:
    """Return one plain sentence for each piece of missing data."""
    gaps: list[str] = []

    for field, label in _CARE_MANAGER_FIELDS.items():
        if not getattr(visit, field).strip():
            gaps.append(f"No {label} on the visit in Care Manager.")
    if not visit.orders_and_activities:
        gaps.append("No orders or activities on the visit in Care Manager.")

    epic = visit.epic
    if epic is None:
        gaps.append("No clinical data was returned from Epic.")
        return gaps

    # An empty or missing allergy list is never "no known allergies".
    if not epic.allergies:
        gaps.append("No allergy data returned from Epic; confirm allergies on arrival.")
    if not epic.conditions:
        gaps.append("No active conditions returned from Epic.")
    if not epic.vitals:
        gaps.append("No vitals returned from Epic.")
    if epic.medications is None:
        gaps.append("No medication data returned from Epic.")

    notes = epic.notes
    if notes is None or not notes.hpi_summary:
        gaps.append("No history of present illness note found since admission.")
    if notes is None or notes.h_and_p is None:
        gaps.append("No H&P found since admission.")
    return gaps
