"""Shared fixtures: the mock visits from the requirements document."""

import json
from pathlib import Path

import pytest

from briefing.models import Visit, parse_visit

FIXTURES = Path(__file__).parent / "fixtures"
MOCK_VISITS_FILE = FIXTURES / "mock-visits.json"


@pytest.fixture(scope="session")
def mock_visits_file() -> Path:
    return MOCK_VISITS_FILE


@pytest.fixture(scope="session")
def raw_visits() -> list[dict]:
    return json.loads(MOCK_VISITS_FILE.read_text(encoding="utf-8"))


def _visit(raw_visits: list[dict], visit_id: str) -> Visit:
    raw = next(v for v in raw_visits if v["visit_id"] == visit_id)
    return parse_visit(json.dumps(raw))


@pytest.fixture
def joe(raw_visits) -> Visit:
    """Joe Smith: the sample JSON. No Epic data at all."""
    return _visit(raw_visits, "visit-1001")


@pytest.fixture
def margaret(raw_visits) -> Visit:
    """Margaret Ellis: the mock briefing. Full Epic data, no H&P, no labs."""
    return _visit(raw_visits, "visit-1002")
