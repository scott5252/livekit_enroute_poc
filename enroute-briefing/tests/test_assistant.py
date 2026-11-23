from briefing.assistant import BriefingAgent
from briefing.config import Settings
from briefing.prompts import NO_PAYLOAD_INSTRUCTIONS
from briefing.sessions import build_session
from briefing.state import BriefingState


def test_agent_has_instructions_and_both_tools(margaret):
    agent = BriefingAgent(margaret)
    assert "Margaret Ellis" in agent.instructions
    tool_names = {tool.info.name for tool in agent.tools}
    assert tool_names == {"get_medication_names", "get_lab_results"}


def test_agent_without_a_visit_uses_the_fallback_prompt():
    assert BriefingAgent(None).instructions == NO_PAYLOAD_INSTRUCTIONS


async def test_pipeline_session_has_all_three_models(margaret, monkeypatch):
    _fake_credentials(monkeypatch)
    state = BriefingState(visit=margaret)
    session = build_session(Settings(), state)
    assert session.stt is not None
    assert session.llm is not None
    assert session.tts is not None
    assert session.userdata is state


async def test_prism_session_has_no_separate_stt_or_tts(margaret, monkeypatch):
    _fake_credentials(monkeypatch)
    settings = Settings(briefing_model="rime-prism")
    session = build_session(settings, BriefingState(visit=margaret))
    assert session.llm is not None
    assert session.stt is None
    assert session.tts is None


def _fake_credentials(monkeypatch):
    # Building a session only needs the variables to exist. Nothing connects.
    monkeypatch.setenv("LIVEKIT_URL", "wss://example.invalid")
    monkeypatch.setenv("LIVEKIT_API_KEY", "test-key")
    monkeypatch.setenv("LIVEKIT_API_SECRET", "test-secret-" + "x" * 32)
