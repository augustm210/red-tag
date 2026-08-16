from typing import Any

from google.cloud import firestore

from red_tag_agent.models import (
    ActionRecord,
    AuditEvent,
    Incident,
    IncidentStatus,
    utc_now,
)


class FirestoreIncidentRepository:
    """Firestore repository with transactional idempotency claims."""

    def __init__(self, project: str | None = None) -> None:
        self._client = firestore.Client(project=project)
        self._incidents = self._client.collection("incidents")
        self._idempotency = self._client.collection("idempotency")

    def create(self, incident: Incident) -> Incident:
        self._incidents.document(incident.id).create(incident.model_dump(mode="json"))
        return incident

    def get(self, incident_id: str) -> Incident | None:
        ref = self._incidents.document(incident_id)
        snapshot = ref.get()
        if not snapshot.exists:
            return None
        data = snapshot.to_dict() or {}
        data["events"] = sorted(
            (item.to_dict() for item in ref.collection("events").stream()),
            key=lambda item: item["occurred_at"],
        )
        data["actions"] = sorted(
            (item.to_dict() for item in ref.collection("actions").stream()),
            key=lambda item: item["created_at"],
        )
        return Incident.model_validate(data)

    def append_event(self, event: AuditEvent) -> None:
        self._incidents.document(event.incident_id).collection("events").document(event.id).create(
            event.model_dump(mode="json")
        )
        self._touch(event.incident_id)

    def update_status(
        self, incident_id: str, status: IncidentStatus, summary: str | None = None
    ) -> Incident:
        values: dict[str, object] = {"status": status.value, "updated_at": utc_now()}
        if summary is not None:
            values["workflow_summary"] = summary
        self._incidents.document(incident_id).update(values)
        incident = self.get(incident_id)
        if incident is None:
            raise KeyError(f"Incident not found: {incident_id}")
        return incident

    def claim_delivery(self, incident_id: str, delivery_id: str) -> bool:
        return self._claim_once(f"delivery:{incident_id}:{delivery_id}", incident_id)

    def release_delivery(self, incident_id: str, delivery_id: str) -> None:
        key = f"delivery:{incident_id}:{delivery_id}".replace("/", "_")
        self._idempotency.document(key).delete()

    def claim_action(self, incident_id: str, action: ActionRecord) -> bool:
        claim_ref = self._idempotency.document(f"action:{action.idempotency_key}")
        action_ref = (
            self._incidents.document(incident_id)
            .collection("actions")
            .document(action.idempotency_key)
        )
        transaction = self._client.transaction()

        @firestore.transactional
        def claim(txn: firestore.Transaction) -> bool:
            if claim_ref.get(transaction=txn).exists:
                return False
            txn.create(
                claim_ref,
                {"incident_id": incident_id, "claimed_at": utc_now()},
            )
            txn.create(action_ref, action.model_dump(mode="json"))
            return True

        return claim(transaction)

    def complete_action(
        self,
        incident_id: str,
        idempotency_key: str,
        evidence: dict[str, Any] | None = None,
    ) -> ActionRecord:
        ref = self._incidents.document(incident_id).collection("actions").document(idempotency_key)
        completed_at = utc_now()
        ref.update(
            {
                "status": "completed",
                "completed_at": completed_at,
                "evidence": evidence or {},
            }
        )
        return ActionRecord.model_validate(ref.get().to_dict())

    def _claim_once(self, key: str, incident_id: str) -> bool:
        ref = self._idempotency.document(key.replace("/", "_"))
        transaction = self._client.transaction()

        @firestore.transactional
        def claim(txn: firestore.Transaction) -> bool:
            if ref.get(transaction=txn).exists:
                return False
            txn.create(ref, {"incident_id": incident_id, "claimed_at": utc_now()})
            return True

        return claim(transaction)

    def _touch(self, incident_id: str) -> None:
        self._incidents.document(incident_id).update(
            {"updated_at": utc_now(), "revision": firestore.Increment(1)}
        )
