import json

import pytest

from briefing.models import PayloadError, parse_visit


def test_parses_both_mock_visits(joe, margaret):
    assert joe.patient_name == "Joe Smith"
    assert joe.age == 86
    assert joe.epic is None
    assert joe.orders_and_activities[0].ordering_provider == "Dr. Emily Chen, MD"

    assert margaret.patient_name == "Margaret Ellis"
    assert len(margaret.epic.allergies) == 2
    assert len(margaret.epic.medications) == 11
    assert margaret.epic.labs is None
    assert margaret.epic.notes.h_and_p is None


@pytest.mark.parametrize("raw", [None, "", "      ", "not json", "[1, 2]", "{}"])
def test_rejects_unusable_metadata(raw):
    with pytest.raises(PayloadError):
        parse_visit(raw)


def test_missing_optional_fields_get_safe_defaults():
    visit = parse_visit('{"visit_id": "v1", "patient_name": "Test Patient"}')
    assert visit.precautions == ""
    assert visit.orders_and_activities == []
    assert visit.epic is None


def test_unknown_fields_are_ignored():
    visit = parse_visit(
        json.dumps({"visit_id": "v1", "patient_name": "Test Patient", "new_field": 1})
    )
    assert visit.visit_id == "v1"


def test_error_message_does_not_leak_the_payload():
    raw = json.dumps({"visit_id": "v1", "patient_name": "Secret Name", "age": "old"})
    with pytest.raises(PayloadError) as excinfo:
        parse_visit(raw)
    assert "Secret Name" not in str(excinfo.value)
    assert "age" in str(excinfo.value)
