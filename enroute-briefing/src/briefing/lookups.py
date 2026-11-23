"""Answers to on-demand questions, as plain functions.

The agent's tools call these. Keeping them free of LiveKit types means they can
be unit tested without a session, a model or a network connection.
"""

from __future__ import annotations

from .models import Visit


def medication_names_text(visit: Visit) -> str:
    """Active medication names, or a plain statement that there are none to give."""
    if visit.epic is None or visit.epic.medications is None:
        return "No medication data was returned from Epic."
    names = [m.name for m in visit.epic.medications]
    if not names:
        return "Epic returned an empty list of active medications."
    return f"{len(names)} active medications: " + "; ".join(names) + "."


def lab_results_text(visit: Visit) -> str:
    """Lab results with the date each was recorded, or a plain statement of none."""
    if visit.epic is None or not visit.epic.labs:
        return "No lab results were returned from Epic."
    parts = []
    for lab in visit.epic.labs:
        flag = f", flagged {lab.interpretation} by Epic" if lab.interpretation else ""
        parts.append(f"{lab.name} {lab.value}, recorded {lab.recorded_at}{flag}")
    return "Lab results: " + "; ".join(parts) + ". Do not interpret these values."
