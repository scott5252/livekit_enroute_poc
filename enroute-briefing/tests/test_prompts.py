from briefing.prompts import NO_PAYLOAD_INSTRUCTIONS, briefing_view, build_instructions


def test_no_visit_uses_the_fallback_prompt():
    assert build_instructions(None) == NO_PAYLOAD_INSTRUCTIONS


def test_prompt_contains_rules_gaps_and_payload(margaret):
    prompt = build_instructions(margaret)
    assert "# Agent rules" in prompt
    assert "- No H&P found since admission." in prompt
    assert '"patient_name": "Margaret Ellis"' in prompt
    assert '"substance": "Penicillin"' in prompt


def test_medication_names_and_labs_stay_out_of_the_prompt(margaret):
    view = briefing_view(margaret)
    assert "medications" not in view["epic"]
    assert "labs" not in view["epic"]
    assert view["epic"]["active_medication_count"] == 11
    assert "Placeholder medication" not in build_instructions(margaret)


def test_visit_without_epic_data(joe):
    prompt = build_instructions(joe)
    assert "- No clinical data was returned from Epic." in prompt
    assert '"epic": null' in prompt


def test_view_does_not_change_the_visit(margaret):
    briefing_view(margaret)
    assert len(margaret.epic.medications) == 11
