from red_tag_agent.models import Incident, IncidentCreate
from red_tag_agent.processor import IncidentProcessor
from red_tag_agent.reliability.executor import SafeActionExecutor
from red_tag_agent.reliability.policy import ActionPolicy
from red_tag_agent.storage.memory import InMemoryIncidentRepository
from red_tag_agent.workflow import LocalIncidentWorkflow


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


def test_failed_workflow_releases_delivery_for_safe_retry() -> None:
    class FailsOnceWorkflow(LocalIncidentWorkflow):
        def __init__(self) -> None:
            self.attempts = 0

        def run(self, incident: Incident):
            self.attempts += 1
            if self.attempts == 1:
                raise RuntimeError("transient model failure")
            return super().run(incident)

    repository = InMemoryIncidentRepository()
    incident = repository.create(
        Incident.from_create(
            IncidentCreate(
                title="Retryable agent failure",
                description="The first model attempt fails before the action boundary.",
                service="windows-disk",
                severity="SEV2",
                requested_action="clear_cache",
            )
        )
    )
    processor = IncidentProcessor(
        repository,
        FailsOnceWorkflow(),
        SafeActionExecutor(repository, ActionPolicy()),
    )

    try:
        processor.process(incident.id, "same-delivery")
    except RuntimeError:
        pass
    else:
        raise AssertionError("The first workflow attempt should fail")

    retry = processor.process(incident.id, "same-delivery")
    assert retry.outcome == "closed"
    stored = repository.get(incident.id)
    assert stored is not None
    assert len(stored.actions) == 1
    assert any(event.event_type == "workflow_attempt_failed_retryable" for event in stored.events)
