import asyncio
import json
from collections.abc import Iterable
from dataclasses import dataclass
from typing import Protocol

from google.adk.apps import App
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

from red_tag_agent.agent import root_agent
from red_tag_agent.models import Incident


@dataclass(frozen=True)
class StageResult:
    stage: str
    summary: str


class IncidentWorkflow(Protocol):
    def run(self, incident: Incident) -> Iterable[StageResult]: ...


class LocalIncidentWorkflow:
    """Deterministic workflow used for offline demos and reliability tests."""

    def run(self, incident: Incident) -> Iterable[StageResult]:
        action = incident.requested_action or "restart"
        yield StageResult(
            "intake",
            f"Normalized {incident.severity} incident for {incident.service}.",
        )
        yield StageResult(
            "investigator",
            f"Correlated reported symptoms with signals: {incident.signals or 'none supplied'}.",
        )
        yield StageResult(
            "resolution_planner",
            f"Proposed {action} with an idempotent execution boundary.",
        )
        yield StageResult(
            "action_executor",
            f"Submitted {action} to the safety policy and action ledger.",
        )
        yield StageResult(
            "closure_verifier",
            "Verified that a terminal action record and audit trail exist.",
        )


class AdkIncidentWorkflow:
    """Runs the real five-node Google ADK workflow against Gemini."""

    def run(self, incident: Incident) -> Iterable[StageResult]:
        return asyncio.run(self._run_async(incident))

    async def _run_async(self, incident: Incident) -> list[StageResult]:
        app_name = "red_tag"
        user_id = "incident-worker"
        session_service = InMemorySessionService()
        session = await session_service.create_session(
            app_name=app_name,
            user_id=user_id,
            session_id=incident.id,
        )
        runner = Runner(
            app=App(name=app_name, root_agent=root_agent),
            session_service=session_service,
        )
        prompt = (
            "Process this incident. Treat only the supplied fields as evidence:\n"
            + json.dumps(incident.model_dump(mode="json"), ensure_ascii=False)
        )
        message = types.Content(role="user", parts=[types.Part(text=prompt)])
        results: list[StageResult] = []
        async for event in runner.run_async(
            user_id=user_id,
            session_id=session.id,
            new_message=message,
        ):
            if not event.content or not event.content.parts:
                continue
            text = "".join(part.text or "" for part in event.content.parts).strip()
            if text:
                results.append(StageResult(event.author, text))
        if not results:
            raise RuntimeError("ADK workflow completed without evidence output")
        return results
