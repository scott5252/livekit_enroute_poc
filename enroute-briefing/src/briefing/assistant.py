"""The agent: its instructions and the tools the language model may call."""

from __future__ import annotations

import logging

from livekit.agents import Agent, RunContext, function_tool

from .lookups import lab_results_text, medication_names_text
from .models import Visit
from .prompts import build_instructions
from .state import BriefingState

logger = logging.getLogger("briefing.assistant")

_NO_VISIT = "The visit details could not be loaded."


class BriefingAgent(Agent):
    """Delivers the en route briefing for one visit and answers follow-ups."""

    def __init__(self, visit: Visit | None) -> None:
        super().__init__(instructions=build_instructions(visit))

    @function_tool
    async def get_medication_names(self, context: RunContext[BriefingState]) -> str:
        """Get the names of the patient's active medications.

        Call this only when the provider asks which medications the patient is on.
        """
        logger.info("tool call: get_medication_names")
        visit = context.userdata.visit
        return medication_names_text(visit) if visit else _NO_VISIT

    @function_tool
    async def get_lab_results(self, context: RunContext[BriefingState]) -> str:
        """Get the patient's lab results, each with the date it was recorded.

        Call this only when the provider asks about lab results.
        """
        logger.info("tool call: get_lab_results")
        visit = context.userdata.visit
        return lab_results_text(visit) if visit else _NO_VISIT
