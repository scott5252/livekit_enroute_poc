import pytest

from briefing.config import ConfigError, load_settings


def test_defaults_when_environment_is_empty():
    settings = load_settings({})
    assert settings.briefing_model == "pipeline"
    assert settings.dev_payload_file is None


def test_reads_and_normalises_values():
    settings = load_settings({"BRIEFING_MODEL": " Rime-Prism ", "RIME_VOICE": "luna"})
    assert settings.briefing_model == "rime-prism"
    assert settings.rime_voice == "luna"


def test_blank_values_fall_back_to_defaults():
    assert load_settings({"LLM_MODEL": " "}).llm_model == load_settings({}).llm_model


def test_unknown_model_fails_fast():
    with pytest.raises(ConfigError, match="BRIEFING_MODEL"):
        load_settings({"BRIEFING_MODEL": "gpt"})
