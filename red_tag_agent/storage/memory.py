from copy import deepcopy
from threading import RLock

from red_tag_agent.models import (
    ActionRecord,
    AuditEvent,
    Incident,
    IncidentStatus,
    utc_now,
)


class InMemoryIncidentRepository:
    """Thread-safe repository used by local development and unit tests."""

    def __init__(self) -> None:
        self._incidents: dict[str, Incident] = {}
        self._deliveries: set[tuple[str, str]] = set()
        self._lock = RLock()

    def create(self, incident: Incident) -> Incident:
        with self._lock:
            if incident.id in self._incidents:
                raise ValueError(f"Incident already exists: {incident.id}")
            self._incidents[incident.id] = deepcopy(incident)
            return deepcopy(incident)

    def get(self, incident_id: str) -> Incident | None:
        with self._lock:
            incident = self._incidents.get(incident_id)
            return deepcopy(incident) if incident else None

    def append_event(self, event: AuditEvent) -> None:
        with self._lock:
            incident = self._require(event.incident_id)
            incident.events.append(deepcopy(event))
            self._touch(incident)

    def update_status(
        self, incident_id: str, status: IncidentStatus, summary: str | None = None
    ) -> Incident:
        with self._lock:
            incident = self._require(incident_id)
            incident.status = status
            if summary is not None:
                incident.workflow_summary = summary
            self._touch(incident)
            return deepcopy(incident)

    def claim_delivery(self, incident_id: str, delivery_id: str) -> bool:
        with self._lock:
            self._require(incident_id)
            key = (incident_id, delivery_id)
            if key in self._deliveries:
                return False
            self._deliveries.add(key)
            return True

    def claim_action(self, incident_id: str, action: ActionRecord) -> bool:
        with self._lock:
            incident = self._require(incident_id)
            if any(item.idempotency_key == action.idempotency_key for item in incident.actions):
                return False
            incident.actions.append(deepcopy(action))
            self._touch(incident)
            return True

    def complete_action(self, incident_id: str, idempotency_key: str) -> ActionRecord:
        with self._lock:
            incident = self._require(incident_id)
            action = next(
                (item for item in incident.actions if item.idempotency_key == idempotency_key),
                None,
            )
            if action is None:
                raise KeyError(f"Action not found: {idempotency_key}")
            action.status = "completed"
            action.completed_at = utc_now()
            self._touch(incident)
            return deepcopy(action)

    def _require(self, incident_id: str) -> Incident:
        incident = self._incidents.get(incident_id)
        if incident is None:
            raise KeyError(f"Incident not found: {incident_id}")
        return incident

    @staticmethod
    def _touch(incident: Incident) -> None:
        incident.updated_at = utc_now()
        incident.revision += 1
