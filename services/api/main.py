import base64
import json
from typing import Any

from fastapi import Depends, FastAPI, HTTPException, status

from red_tag_agent.config import get_settings
from red_tag_agent.dispatch import IncidentDispatcher
from red_tag_agent.models import (
    AuditEvent,
    Incident,
    IncidentCreate,
    ProcessRequest,
    ProcessResult,
)
from red_tag_agent.processor import IncidentProcessor
from red_tag_agent.storage.base import IncidentRepository
from services.api.dependencies import get_dispatcher, get_processor, get_repository

app = FastAPI(
    title="Red Tag Incident Command API",
    version="0.1.0",
    description="Evidence-first, idempotent multi-agent incident response.",
)


def require_api_role() -> None:
    if get_settings().service_role not in {"all", "api"}:
        raise HTTPException(status_code=404, detail="Not found")


def require_worker_role() -> None:
    if get_settings().service_role not in {"all", "worker"}:
        raise HTTPException(status_code=404, detail="Not found")


@app.get("/healthz")
def healthz() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/v1/incidents", response_model=Incident, status_code=status.HTTP_201_CREATED)
def create_incident(
    request: IncidentCreate,
    _: None = Depends(require_api_role),
    repository: IncidentRepository = Depends(get_repository),
    dispatcher: IncidentDispatcher = Depends(get_dispatcher),
) -> Incident:
    incident = repository.create(Incident.from_create(request))
    repository.append_event(
        AuditEvent(
            incident_id=incident.id,
            event_type="incident_created",
            actor="public-api",
            data={"severity": incident.severity.value, "service": incident.service},
        )
    )
    try:
        message_id = dispatcher.dispatch(incident.id)
        repository.append_event(
            AuditEvent(
                incident_id=incident.id,
                event_type="incident_dispatched",
                actor="public-api",
                data={"message_id": message_id},
            )
        )
    except Exception as exc:
        repository.append_event(
            AuditEvent(
                incident_id=incident.id,
                event_type="incident_dispatch_failed",
                actor="public-api",
                data={"error_type": type(exc).__name__},
            )
        )
        raise HTTPException(status_code=503, detail="Incident dispatch failed") from exc
    current = repository.get(incident.id)
    if current is None:
        raise HTTPException(status_code=500, detail="Incident persistence failed")
    return current


@app.get("/v1/incidents/{incident_id}", response_model=Incident)
def get_incident(
    incident_id: str,
    _: None = Depends(require_api_role),
    repository: IncidentRepository = Depends(get_repository),
) -> Incident:
    incident = repository.get(incident_id)
    if incident is None:
        raise HTTPException(status_code=404, detail="Incident not found")
    return incident


@app.post("/v1/incidents/{incident_id}/process", response_model=ProcessResult)
def process_incident(
    incident_id: str,
    request: ProcessRequest,
    _: None = Depends(require_worker_role),
    processor: IncidentProcessor = Depends(get_processor),
) -> ProcessResult:
    try:
        return processor.process(incident_id, request.delivery_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@app.post("/internal/pubsub/incidents", status_code=status.HTTP_200_OK)
def receive_pubsub(
    envelope: dict[str, Any],
    _: None = Depends(require_worker_role),
    processor: IncidentProcessor = Depends(get_processor),
) -> dict[str, str]:
    try:
        message = envelope["message"]
        payload = json.loads(base64.b64decode(message["data"]).decode("utf-8"))
        incident_id = payload["incident_id"]
        delivery_id = message.get("messageId") or message.get("message_id")
        if not delivery_id:
            raise ValueError("Pub/Sub message ID is required")
        result = processor.process(incident_id, delivery_id)
        return {"outcome": result.outcome}
    except (KeyError, ValueError, json.JSONDecodeError) as exc:
        raise HTTPException(status_code=400, detail=f"Invalid Pub/Sub envelope: {exc}") from exc
