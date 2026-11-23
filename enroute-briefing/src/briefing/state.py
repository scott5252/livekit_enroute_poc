"""Per-session state, shared between the entrypoint, the agent and its tools."""

from __future__ import annotations

from dataclasses import dataclass

from .models import Visit


@dataclass
class BriefingState:
    """Attached to the AgentSession as userdata. One instance per briefing."""

    visit: Visit | None = None
