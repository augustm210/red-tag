from red_tag_agent.models import AuditEvent, IncidentStatus, ProcessResult
from red_tag_agent.reliability.executor import SafeActionExecutor
from red_tag_agent.storage.base import IncidentRepository
from red_tag_agent.workflow import IncidentWorkflow


class IncidentProcessor:
    def __init__(
        self,
        repository: IncidentRepository,
        workflow: IncidentWorkflow,
        executor: SafeActionExecutor,
    ) -> None:
        self._repository = repository
        self._workflow = workflow
        self._executor = executor

    def process(self, incident_id: str, delivery_id: str) -> ProcessResult:
        incident = self._repository.get(incident_id)
        if incident is None:
            raise KeyError(f"Incident not found: {incident_id}")

        if not self._repository.claim_delivery(incident_id, delivery_id):
            self._repository.append_event(
                AuditEvent(
                    incident_id=incident_id,
                    event_type="duplicate_delivery_blocked",
                    actor="incident-processor",
                    data={"delivery_id": delivery_id},
                )
            )
            current = self._repository.get(incident_id)
            if current is None:
                raise KeyError(incident_id)
            return ProcessResult(
                incident_id=incident_id,
                outcome="duplicate_delivery_blocked",
                status=current.status,
                action=current.actions[-1] if current.actions else None,
                workflow_summary=current.workflow_summary,
            )

        try:
            if incident.status in {IncidentStatus.CLOSED, IncidentStatus.MITIGATED}:
                return ProcessResult(
                    incident_id=incident_id,
                    outcome="already_terminal",
                    status=incident.status,
                    action=incident.actions[-1] if incident.actions else None,
                    workflow_summary=incident.workflow_summary,
                )

            self._repository.update_status(incident_id, IncidentStatus.INVESTIGATING)
            summaries: list[str] = []
            for result in self._workflow.run(incident):
                summaries.append(f"{result.stage}: {result.summary}")
                self._repository.append_event(
                    AuditEvent(
                        incident_id=incident_id,
                        event_type="agent_stage_completed",
                        actor=result.stage,
                        data={"summary": result.summary},
                    )
                )

            action = self._executor.execute(incident, incident.requested_action or "restart")
            verification = self._workflow.verify(incident, action)
            summaries.append(f"{verification.stage}: {verification.summary}")
            self._repository.append_event(
                AuditEvent(
                    incident_id=incident_id,
                    event_type="agent_stage_completed",
                    actor=verification.stage,
                    data={"summary": verification.summary},
                )
            )
            summary = " | ".join(summaries)
            if action.status == "awaiting_approval":
                final_status = IncidentStatus.AWAITING_APPROVAL
                outcome = "human_approval_required"
            else:
                final_status = IncidentStatus.CLOSED
                outcome = "closed"

            self._repository.update_status(incident_id, final_status, summary)
            self._repository.append_event(
                AuditEvent(
                    incident_id=incident_id,
                    event_type="incident_processing_completed",
                    actor="closure-verifier",
                    data={"outcome": outcome, "action_status": action.status},
                )
            )
            return ProcessResult(
                incident_id=incident_id,
                outcome=outcome,
                status=final_status,
                action=action,
                workflow_summary=summary,
            )
        except Exception as exc:
            self._repository.release_delivery(incident_id, delivery_id)
            self._repository.append_event(
                AuditEvent(
                    incident_id=incident_id,
                    event_type="workflow_attempt_failed_retryable",
                    actor="incident-processor",
                    data={"delivery_id": delivery_id, "error_type": type(exc).__name__},
                )
            )
            raise
