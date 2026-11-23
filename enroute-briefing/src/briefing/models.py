"""Typed models for the visit payload the server sends as job metadata.

Field names follow the requirements document. Validation happens once, at the
edge, so every other module can trust the shape of the data it is given.
"""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, ValidationError


class PayloadError(ValueError):
    """The job metadata is missing, is not JSON, or is not a visit payload."""


class _Model(BaseModel):
    # Ignore unknown fields so the server can add data without breaking the agent.
    model_config = ConfigDict(extra="ignore")


class Contact(_Model):
    name: str
    relationship: str = ""
    phone: str = ""


class OrderActivity(_Model):
    activity: str
    ordering_provider: str = ""


class CareTeamMember(_Model):
    name: str
    role: str = ""


class CustomerSponsor(_Model):
    name: str = ""
    phone: str = ""


class Allergy(_Model):
    substance: str
    clinical_status: str = ""
    criticality: str | None = None
    reactions: list[str] = []


class Medication(_Model):
    name: str
    status: str = ""


class Condition(_Model):
    name: str
    clinical_status: str = ""
    onset: str | None = None


class Observation(_Model):
    """One vital sign or lab result. recorded_at must always be spoken with it."""

    name: str
    value: str
    recorded_at: str
    interpretation: str | None = None


class HistoryAndPhysical(_Model):
    date: str
    summary: str = ""


class ClinicalNotes(_Model):
    hpi_summary: str | None = None
    hpi_date: str | None = None
    precautions: str | None = None
    h_and_p: HistoryAndPhysical | None = None


class EpicData(_Model):
    """Clinical history from Epic. None means Epic returned nothing for that item,
    which is different from an empty list."""

    allergies: list[Allergy] | None = None
    medications: list[Medication] | None = None
    conditions: list[Condition] | None = None
    vitals: list[Observation] | None = None
    labs: list[Observation] | None = None
    notes: ClinicalNotes | None = None


class Visit(_Model):
    visit_id: str

    # Care Manager patient summary
    patient_name: str
    age: int | None = None
    sex: str = ""
    patient_address: str = ""
    visit_reason: str = ""
    visit_status: str = ""
    featured_note: str = ""
    home_access: str = ""
    precautions: str = ""
    orders_and_activities: list[OrderActivity] = []
    nursing_instructions: str = ""
    schedule_start_time: str = ""
    estimated_visit_duration: str = ""
    care_team: list[CareTeamMember] = []
    customer_sponsor: CustomerSponsor = CustomerSponsor()
    sponsor: str = ""

    # Cesia patient profile
    patient_language: str = ""
    non_verbal_patient: bool = False
    gender_identity: str = ""
    sexual_orientation: str = ""
    race: str = ""
    ethnicity: str = ""
    date_of_admission: str = ""
    additional_patient_contacts: list[Contact] = []

    # Epic clinical history. None means no Epic data at all.
    epic: EpicData | None = None


def parse_visit(raw: str | None) -> Visit:
    """Validate a JSON string and return a Visit, or raise PayloadError.

    The error message never includes the payload, so it is safe to log.
    """
    if not raw or not raw.strip():
        raise PayloadError("job metadata is empty")
    try:
        return Visit.model_validate_json(raw)
    except ValidationError as err:
        problems = "; ".join(
            f"{'.'.join(str(part) for part in e['loc']) or 'payload'}: {e['type']}"
            for e in err.errors()[:5]
        )
        raise PayloadError(f"job metadata is not a valid visit: {problems}") from None
