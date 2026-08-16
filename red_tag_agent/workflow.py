import asyncio
import json
from collections.abc import Iterable
from dataclasses import dataclass
from typing import Protocol

from google.adk.apps import App
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

from red_tag_agent.agent import root_agent, verification_root_agent
from red_tag_agent.models import ActionRecord, Incident


@dataclass(frozen=True)
class StageResult:
    stage: str
    summary: str


class IncidentWorkflow(Protocol):
    def run(self, incident: Incident) -> Iterable[StageResult]: ...

    def verify(self, incident: Incident, action: ActionRecord) -> StageResult: ...


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
    def verify(self, incident: Incident, action: ActionRecord) -> StageResult:
        return StageResult(
            "closure_verifier",
            f"Verified {action.status} action {action.idempotency_key} after execution.",
        )


class AdkIncidentWorkflow:
    """Runs the real five-node Google ADK workflow against Gemini."""

    def run(self, incident: Incident) -> Iterable[StageResult]:
        prompt = (
            "Process this incident. Treat only the supplied fields as evidence:\n"
            + json.dumps(incident.model_dump(mode="json"), ensure_ascii=False)
        )
        return asyncio.run(
            self._run_async(
                app_name="red_tag_reasoning",
                session_id=incident.id,
                agent=root_agent,
                prompt=prompt,
            )
        )

    def verify(self, incident: Incident, action: ActionRecord) -> StageResult:
        prompt = (
            "Verify the post-execution control-plane result below. The durable action "
            "record is authoritative for this safe demo adapter. Confirm closure only "
            "when status is completed and an idempotency key and completion time exist. "
            "Do not claim physical disk recovery; explicitly identify that as the local "
            "executor's separate verification scope.\n"
            + json.dumps(
                {
                    "incident_id": incident.id,
                    "verification_scope": "cloud_control_plane",
                    "action": action.model_dump(mode="json"),
                },
                ensure_ascii=False,
            )
        )
        results = asyncio.run(
            self._run_async(
                app_name="red_tag_verification",
                session_id=f"{incident.id}-verify",
                agent=verification_root_agent,
                prompt=prompt,
            )
        )
        if not results:
            raise RuntimeError("Closure verifier completed without evidence output")
        return StageResult("closure_verifier", results[-1].summary)

    async def _run_async(
        self,
        *,
        app_name: str,
        session_id: str,
        agent,
        prompt: str,
    ) -> list[StageResult]:
        user_id = "incident-worker"
        session_service = InMemorySessionService()
        session = await session_service.create_session(
            app_name=app_name,
            user_id=user_id,
            session_id=session_id,
        )
        runner = Runner(
            app=App(name=app_name, root_agent=agent),
            session_service=session_service,
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
