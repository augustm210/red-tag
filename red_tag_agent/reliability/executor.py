import hashlib

from red_tag_agent.models import ActionRecord, AuditEvent, Incident
from red_tag_agent.reliability.policy import ActionPolicy
from red_tag_agent.storage.base import IncidentRepository


class SafeActionExecutor:
    def __init__(self, repository: IncidentRepository, policy: ActionPolicy) -> None:
        self._repository = repository
        self._policy = policy

    def execute(self, incident: Incident, action_name: str) -> ActionRecord:
        decision = self._policy.evaluate(incident, action_name)
        key = self.idempotency_key(incident.id, decision.action, incident.service)
        record = ActionRecord(
            idempotency_key=key,
            action=decision.action,
            target=incident.service,
            status="awaiting_approval" if decision.requires_approval else "claimed",
            reason=decision.reason,
        )

        if not decision.allowed:
            self._repository.claim_action(incident.id, record)
            return record

        if not self._repository.claim_action(incident.id, record):
            existing = self._repository.get(incident.id)
            if existing is None:
                raise KeyError(incident.id)
            previous = next(item for item in existing.actions if item.idempotency_key == key)
            self._repository.append_event(
                AuditEvent(
                    incident_id=incident.id,
                    event_type="duplicate_action_blocked",
                    actor="safe-action-executor",
                    data={"idempotency_key": key, "action": decision.action},
                )
            )
            return previous

        # The first slice uses a safe simulated operational adapter. A real
        # Cloud Run/GKE adapter replaces this boundary without changing the
        # idempotency contract.
        return self._repository.complete_action(incident.id, key)

    @staticmethod
    def idempotency_key(incident_id: str, action: str, target: str) -> str:
        raw = f"{incident_id}:{action}:{target}".encode()
        return hashlib.sha256(raw).hexdigest()[:32]
