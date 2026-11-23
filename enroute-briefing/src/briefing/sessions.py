"""Build the voice session for the configured model stack."""

from __future__ import annotations

from livekit.agents import AgentSession, TurnHandlingOptions, inference

from .config import RIME_PRISM, Settings
from .state import BriefingState


def build_session(settings: Settings, state: BriefingState) -> AgentSession:
    """Create an AgentSession. The models are the only thing that differs."""
    if settings.briefing_model == RIME_PRISM:
        # Rime Prism listens and speaks in one model, through LiveKit Inference.
        # It does its own turn detection, so no STT, TTS or turn detector is set.
        return AgentSession[BriefingState](
            userdata=state,
            llm=inference.RealtimeModel(model="rime/prism", voice=settings.rime_voice),
        )

    return AgentSession[BriefingState](
        userdata=state,
        # Ears: speech to text.
        stt=inference.STT(model=settings.stt_model, language=settings.stt_language),
        # Brain: the language model that follows the briefing rules.
        llm=inference.LLM(model=settings.llm_model),
        # Voice: text to speech.
        tts=inference.TTS(model=settings.tts_model, voice=settings.tts_voice),
        # Decides when the provider has finished speaking.
        turn_handling=TurnHandlingOptions(
            turn_detection=inference.TurnDetector(),
        ),
    )
