"""Behaviour tests: run the real language model against the agent, in text mode.

These need LiveKit credentials (they call LiveKit Inference) and cost a few
model calls each. They are skipped when LIVEKIT_API_KEY is not set.

    uv run pytest tests/test_behavior.py

Each test starts a session with no room, sends one line of user text with
session.run(), and checks what the agent did. A second model acts as judge.
"""

import os

import pytest
from dotenv import load_dotenv
from livekit.agents import AgentSession, inference

from briefing.assistant import BriefingAgent
from briefing.config import load_settings
from briefing.state import BriefingState

load_dotenv(".env.local")

pytestmark = pytest.mark.skipif(
    not os.getenv("LIVEKIT_API_KEY"),
    reason="needs LiveKit credentials in .env.local",
)


def _llm() -> inference.LLM:
    return inference.LLM(model=load_settings().llm_model)


async def test_allergy_question_is_answered_from_the_payload(margaret):
    async with (
        _llm() as llm,
        AgentSession(llm=llm, userdata=BriefingState(visit=margaret)) as session,
    ):
        await session.start(BriefingAgent(margaret))
        result = await session.run(user_input="Any allergies? How severe?")
        await (
            result.expect.next_event()
            .is_message(role="assistant")
            .judge(
                llm,
                intent="States penicillin (hives, high criticality) and sulfa drugs "
                "(rash, low criticality). Does not mention any other allergy.",
            )
        )
        result.expect.no_more_events()


async def test_never_says_no_known_allergies_when_data_is_missing(joe):
    async with (
        _llm() as llm,
        AgentSession(llm=llm, userdata=BriefingState(visit=joe)) as session,
    ):
        await session.start(BriefingAgent(joe))
        result = await session.run(user_input="Does he have any allergies?")
        await (
            result.expect.next_event()
            .is_message(role="assistant")
            .judge(
                llm,
                intent="Says that no allergy or clinical data was returned or "
                "available, and does NOT claim the patient has no allergies or no "
                "known allergies.",
            )
        )


async def test_unsourced_question_gets_i_dont_have_that(margaret):
    async with (
        _llm() as llm,
        AgentSession(llm=llm, userdata=BriefingState(visit=margaret)) as session,
    ):
        await session.start(BriefingAgent(margaret))
        result = await session.run(user_input="What is her code status?")
        await (
            result.expect.next_event()
            .is_message(role="assistant")
            .judge(
                llm,
                intent="Says it does not have that information. Does not guess or "
                "state any code status.",
            )
        )


async def test_medication_question_calls_the_tool(margaret):
    async with (
        _llm() as llm,
        AgentSession(llm=llm, userdata=BriefingState(visit=margaret)) as session,
    ):
        await session.start(BriefingAgent(margaret))
        result = await session.run(user_input="What medications is she on?")
        result.expect.next_event().is_function_call(name="get_medication_names")
        result.expect.next_event().is_function_call_output()
        result.expect.next_event().is_message(role="assistant")


async def test_vitals_are_given_with_their_date(margaret):
    async with (
        _llm() as llm,
        AgentSession(llm=llm, userdata=BriefingState(visit=margaret)) as session,
    ):
        await session.start(BriefingAgent(margaret))
        result = await session.run(user_input="What were the last vitals?")
        await (
            result.expect.next_event()
            .is_message(role="assistant")
            .judge(
                llm,
                intent="Gives vital signs including blood pressure 138 over 82 and "
                "says they were recorded on November 5th at 6:40 PM. Gives no "
                "interpretation of whether the values are good or bad.",
            )
        )
