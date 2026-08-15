from red_tag_agent.models import Incident, IncidentCreate
from red_tag_agent.reliability.executor import SafeActionExecutor
from red_tag_agent.reliability.policy import ActionPolicy
from red_tag_agent.storage.memory import InMemoryIncidentRepository


def test_same_action_is_executed_exactly_once() -> None:
    repository = InMemoryIncidentRepository()
    incident = repository.create(
        Incident.from_create(
            IncidentCreate(
                title="Repeated worker delivery",
                description="The worker receives the same mitigation more than once.",
                service="checkout",
                severity="SEV2",
                requested_action="rollback",
            )
        )
    )
    executor = SafeActionExecutor(repository, ActionPolicy())

    first = executor.execute(incident, "rollback")
    second = executor.execute(incident, "rollback")

    assert first.idempotency_key == second.idempotency_key
    assert first.status == second.status == "completed"
    stored = repository.get(incident.id)
    assert stored is not None
    assert len(stored.actions) == 1
    assert any(event.event_type == "duplicate_action_blocked" for event in stored.events)
