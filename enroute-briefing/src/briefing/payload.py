"""Find the visit for a job: from job metadata, or from a file in development."""

from __future__ import annotations

import json
import logging
from pathlib import Path

from .config import Settings
from .models import PayloadError, Visit, parse_visit

logger = logging.getLogger("briefing.payload")


def load_visit(metadata: str | None, settings: Settings) -> Visit:
    """Return the visit for this job, or raise PayloadError.

    Normal path: the server attached the visit as job metadata at dispatch.
    Development path: no metadata arrived (console mode, or the Agent Console in
    the dashboard) and DEV_PAYLOAD_FILE names a JSON file to read instead.
    """
    if metadata and metadata.strip():
        return parse_visit(metadata)

    if settings.dev_payload_file:
        logger.warning(
            "no job metadata; using DEV_PAYLOAD_FILE (development only): visit=%s",
            settings.dev_visit_id,
        )
        return _load_from_file(Path(settings.dev_payload_file), settings.dev_visit_id)

    raise PayloadError("job metadata is empty")


def _load_from_file(path: Path, visit_id: str) -> Visit:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except OSError as err:
        raise PayloadError(f"cannot read {path}: {err.strerror}") from None
    except json.JSONDecodeError as err:
        raise PayloadError(f"{path} is not valid JSON: line {err.lineno}") from None

    # The file may hold one visit or a list of visits.
    visits = data if isinstance(data, list) else [data]
    for item in visits:
        if isinstance(item, dict) and item.get("visit_id") == visit_id:
            return parse_visit(json.dumps(item))
    raise PayloadError(f"no visit {visit_id!r} in {path}")
