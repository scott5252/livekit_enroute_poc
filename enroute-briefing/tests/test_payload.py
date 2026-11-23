import json

import pytest

from briefing.config import Settings
from briefing.models import PayloadError
from briefing.payload import load_visit


def test_metadata_is_used_when_present(raw_visits):
    visit = load_visit(json.dumps(raw_visits[0]), Settings())
    assert visit.visit_id == "visit-1001"


def test_no_metadata_and_no_dev_file_is_an_error():
    with pytest.raises(PayloadError, match="empty"):
        load_visit("", Settings())


def test_dev_file_is_used_only_when_metadata_is_missing(raw_visits, mock_visits_file):
    settings = Settings(
        dev_payload_file=str(mock_visits_file), dev_visit_id="visit-1002"
    )
    assert load_visit(None, settings).patient_name == "Margaret Ellis"
    assert load_visit(json.dumps(raw_visits[0]), settings).patient_name == "Joe Smith"


def test_dev_file_problems_are_reported(tmp_path, mock_visits_file):
    missing = Settings(dev_payload_file=str(tmp_path / "nope.json"))
    with pytest.raises(PayloadError, match="cannot read"):
        load_visit(None, missing)

    bad = tmp_path / "bad.json"
    bad.write_text("{ not json", encoding="utf-8")
    with pytest.raises(PayloadError, match="not valid JSON"):
        load_visit(None, Settings(dev_payload_file=str(bad)))

    unknown = Settings(dev_payload_file=str(mock_visits_file), dev_visit_id="visit-9")
    with pytest.raises(PayloadError, match="no visit"):
        load_visit(None, unknown)
