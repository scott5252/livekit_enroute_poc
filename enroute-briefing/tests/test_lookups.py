from briefing.lookups import lab_results_text, medication_names_text
from briefing.models import Observation


def test_medication_names(margaret, joe):
    text = medication_names_text(margaret)
    assert text.startswith("11 active medications: ")
    assert "Placeholder medication 11" in text
    assert medication_names_text(joe) == "No medication data was returned from Epic."


def test_lab_results_when_none_returned(margaret, joe):
    assert lab_results_text(margaret) == "No lab results were returned from Epic."
    assert lab_results_text(joe) == "No lab results were returned from Epic."


def test_lab_results_always_carry_their_date(margaret):
    lab = Observation(
        name="WBC",
        value="14.2 K/uL",
        recorded_at="November 5, 7:15 AM",
        interpretation="High",
    )
    epic = margaret.epic.model_copy(update={"labs": [lab]})
    text = lab_results_text(margaret.model_copy(update={"epic": epic}))
    assert "WBC 14.2 K/uL, recorded November 5, 7:15 AM, flagged High by Epic" in text
