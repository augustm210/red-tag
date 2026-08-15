import json
from typing import Protocol

from google.cloud import pubsub_v1


class IncidentDispatcher(Protocol):
    def dispatch(self, incident_id: str) -> str: ...


class ManualIncidentDispatcher:
    """Local dispatcher: the caller explicitly invokes the processing endpoint."""

    def dispatch(self, incident_id: str) -> str:
        return f"manual:{incident_id}"


class PubSubIncidentDispatcher:
    def __init__(self, project: str, topic: str) -> None:
        self._publisher = pubsub_v1.PublisherClient()
        self._topic_path = self._publisher.topic_path(project, topic)

    def dispatch(self, incident_id: str) -> str:
        payload = json.dumps({"incident_id": incident_id}).encode("utf-8")
        return self._publisher.publish(
            self._topic_path,
            payload,
            incident_id=incident_id,
            event_type="incident.created",
        ).result(timeout=30)
