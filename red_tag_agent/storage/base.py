from typing import Any, Protocol

from red_tag_agent.models import ActionRecord, AuditEvent, Incident, IncidentStatus


class IncidentRepository(Protocol):
    def create(self, incident: Incident) -> Incident: ...

    def get(self, incident_id: str) -> Incident | None: ...

    def append_event(self, event: AuditEvent) -> None: ...

    def update_status(
        self, incident_id: str, status: IncidentStatus, summary: str | None = None
    ) -> Incident: ...

    def claim_delivery(self, incident_id: str, delivery_id: str) -> bool: ...

    def claim_action(self, incident_id: str, action: ActionRecord) -> bool: ...

    def complete_action(
        self,
        incident_id: str,
        idempotency_key: str,
        evidence: dict[str, Any] | None = None,
    ) -> ActionRecord: ...
