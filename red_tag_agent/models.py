from __future__ import annotations

from datetime import UTC, datetime
from enum import StrEnum
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, Field


def utc_now() -> datetime:
    return datetime.now(UTC)


class Severity(StrEnum):
    SEV1 = "SEV1"
    SEV2 = "SEV2"
    SEV3 = "SEV3"
    SEV4 = "SEV4"


class IncidentStatus(StrEnum):
    CREATED = "created"
    INVESTIGATING = "investigating"
    AWAITING_APPROVAL = "awaiting_approval"
    MITIGATED = "mitigated"
    CLOSED = "closed"
    FAILED = "failed"


class IncidentCreate(BaseModel):
    title: str = Field(min_length=5, max_length=160)
    description: str = Field(min_length=10, max_length=4000)
    service: str = Field(min_length=2, max_length=80)
    severity: Severity
    requested_action: str | None = Field(default=None, max_length=80)
    signals: dict[str, Any] = Field(default_factory=dict)


class AuditEvent(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    incident_id: str
    event_type: str
    actor: str
    occurred_at: datetime = Field(default_factory=utc_now)
    data: dict[str, Any] = Field(default_factory=dict)


class ActionRecord(BaseModel):
    idempotency_key: str
    action: str
    target: str
    status: str
    reason: str
    evidence: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=utc_now)
    completed_at: datetime | None = None


class Incident(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    title: str
    description: str
    service: str
    severity: Severity
    requested_action: str | None = None
    signals: dict[str, Any] = Field(default_factory=dict)
    status: IncidentStatus = IncidentStatus.CREATED
    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)
    revision: int = 1
    workflow_summary: str | None = None
    events: list[AuditEvent] = Field(default_factory=list)
    actions: list[ActionRecord] = Field(default_factory=list)

    @classmethod
    def from_create(cls, request: IncidentCreate) -> Incident:
        return cls(**request.model_dump())


class ProcessRequest(BaseModel):
    delivery_id: str = Field(min_length=3, max_length=200)


class ProcessResult(BaseModel):
    incident_id: str
    outcome: str
    status: IncidentStatus
    action: ActionRecord | None = None
    workflow_summary: str | None = None
