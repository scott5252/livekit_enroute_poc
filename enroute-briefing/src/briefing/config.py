"""Settings for the agent, read once from environment variables at startup.

Everything that can differ between a laptop, a test run and production lives
here, so the rest of the code never calls os.getenv directly.
"""

from __future__ import annotations

import os
from collections.abc import Mapping
from dataclasses import dataclass

# The dispatch name. The server asks LiveKit for an agent with exactly this name.
AGENT_NAME = "enroute-briefing"

PIPELINE = "pipeline"
RIME_PRISM = "rime-prism"
VALID_MODELS = (PIPELINE, RIME_PRISM)


class ConfigError(ValueError):
    """Raised at startup when an environment variable has an unusable value."""


@dataclass(frozen=True)
class Settings:
    # Which voice stack to use: "pipeline" (STT + LLM + TTS) or "rime-prism".
    briefing_model: str = PIPELINE

    # Pipeline models, all served through LiveKit Inference.
    stt_model: str = "assemblyai/universal-3-6-pro"
    stt_language: str = "en"
    llm_model: str = "google/gemma-4-31b-it"
    tts_model: str = "fishaudio/s2.1-pro"
    tts_voice: str = "fa4c9eb3dccc4806b382b40d61c6b10a"

    # Voice for the Rime Prism real-time model.
    rime_voice: str = "astra"

    # Development only: a JSON file to use when a job arrives with no metadata,
    # for example in console mode. Leave unset in production.
    dev_payload_file: str | None = None
    dev_visit_id: str = "visit-1002"


def load_settings(env: Mapping[str, str] | None = None) -> Settings:
    """Build Settings from the environment, failing fast on bad values."""
    env = os.environ if env is None else env
    defaults = Settings()

    def get(name: str, default: str) -> str:
        # A variable that is unset or blank falls back to the default.
        return (env.get(name) or "").strip() or default

    briefing_model = get("BRIEFING_MODEL", defaults.briefing_model).lower()
    if briefing_model not in VALID_MODELS:
        raise ConfigError(
            f"BRIEFING_MODEL must be one of {VALID_MODELS}, got {briefing_model!r}"
        )

    return Settings(
        briefing_model=briefing_model,
        stt_model=get("STT_MODEL", defaults.stt_model),
        stt_language=get("STT_LANGUAGE", defaults.stt_language),
        llm_model=get("LLM_MODEL", defaults.llm_model),
        tts_model=get("TTS_MODEL", defaults.tts_model),
        tts_voice=get("TTS_VOICE", defaults.tts_voice),
        rime_voice=get("RIME_VOICE", defaults.rime_voice),
        dev_payload_file=get("DEV_PAYLOAD_FILE", "") or None,
        dev_visit_id=get("DEV_VISIT_ID", defaults.dev_visit_id),
    )
