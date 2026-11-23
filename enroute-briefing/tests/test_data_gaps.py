from briefing.data_gaps import find_data_gaps
from briefing.models import EpicData


def test_no_epic_data_is_one_clear_gap(joe):
    assert find_data_gaps(joe) == ["No clinical data was returned from Epic."]


def test_margaret_gaps_match_the_mock_record(margaret):
    assert find_data_gaps(margaret) == [
        "No history of present illness note found since admission.",
        "No H&P found since admission.",
    ]


def test_missing_and_empty_allergies_are_both_gaps(margaret):
    for allergies in (None, []):
        epic = margaret.epic.model_copy(update={"allergies": allergies})
        visit = margaret.model_copy(update={"epic": epic})
        gaps = find_data_gaps(visit)
        assert any("No allergy data returned" in gap for gap in gaps)
        assert not any("no known allergies" in gap.lower() for gap in gaps)


def test_empty_care_manager_fields_are_gaps(margaret):
    visit = margaret.model_copy(
        update={"featured_note": " ", "orders_and_activities": [], "epic": EpicData()}
    )
    gaps = find_data_gaps(visit)
    assert "No featured note on the visit in Care Manager." in gaps
    assert "No orders or activities on the visit in Care Manager." in gaps
    assert "No medication data returned from Epic." in gaps
    assert "No vitals returned from Epic." in gaps
