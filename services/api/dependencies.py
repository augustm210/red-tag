from functools import lru_cache

from red_tag_agent.config import get_settings
from red_tag_agent.dispatch import (
    IncidentDispatcher,
    ManualIncidentDispatcher,
    PubSubIncidentDispatcher,
)
from red_tag_agent.processor import IncidentProcessor
from red_tag_agent.reliability.executor import SafeActionExecutor
from red_tag_agent.reliability.policy import ActionPolicy
from red_tag_agent.storage.base import IncidentRepository
from red_tag_agent.storage.firestore import FirestoreIncidentRepository
from red_tag_agent.storage.memory import InMemoryIncidentRepository
from red_tag_agent.workflow import AdkIncidentWorkflow, LocalIncidentWorkflow


@lru_cache
def get_repository() -> IncidentRepository:
    settings = get_settings()
    if settings.repository_backend == "firestore":
        return FirestoreIncidentRepository(project=settings.google_cloud_project)
    return InMemoryIncidentRepository()


@lru_cache
def get_dispatcher() -> IncidentDispatcher:
    settings = get_settings()
    if settings.dispatch_backend == "pubsub":
        if not settings.google_cloud_project:
            raise RuntimeError("RED_TAG_GOOGLE_CLOUD_PROJECT is required for Pub/Sub")
        return PubSubIncidentDispatcher(
            project=settings.google_cloud_project,
            topic=settings.incident_topic,
        )
    return ManualIncidentDispatcher()


@lru_cache
def get_processor() -> IncidentProcessor:
    settings = get_settings()
    repository = get_repository()
    workflow = AdkIncidentWorkflow() if settings.agent_mode == "adk" else LocalIncidentWorkflow()
    return IncidentProcessor(
        repository=repository,
        workflow=workflow,
        executor=SafeActionExecutor(repository, ActionPolicy()),
    )
