from google.adk.agents import LlmAgent
from google.adk.workflow import START, Workflow

from red_tag_agent.config import get_settings

settings = get_settings()

intake_agent = LlmAgent(
    name="intake_agent",
    model=settings.model,
    instruction=(
        "Normalize the incident. Identify service, severity, symptoms, missing "
        "facts, and safety constraints. Do not invent evidence."
    ),
    output_key="intake_report",
    mode="single_turn",
)

investigator_agent = LlmAgent(
    name="investigator_agent",
    model=settings.model,
    instruction=(
        "Investigate the incident using the intake report in {intake_report}. "
        "Separate observed evidence from hypotheses and rank likely causes."
    ),
    output_key="investigation_report",
    mode="single_turn",
)

planner_agent = LlmAgent(
    name="resolution_planner",
    model=settings.model,
    instruction=(
        "Create the smallest reversible mitigation plan using "
        "{investigation_report}. Include risk, rollback, and verification steps."
    ),
    output_key="resolution_plan",
    mode="single_turn",
)

executor_agent = LlmAgent(
    name="action_executor",
    model=settings.model,
    instruction=(
        "Review {resolution_plan} against safety policy. Never claim an action "
        "ran unless a tool record proves it. Return the proposed action only."
    ),
    output_key="execution_decision",
    mode="single_turn",
)

verifier_agent = LlmAgent(
    name="closure_verifier",
    model=settings.model,
    instruction=(
        "Verify the post-execution record supplied in the user message against "
        "the available evidence. State whether the scoped incident may close "
        "and list remaining uncertainty. Never invent execution evidence."
    ),
    output_key="closure_report",
    mode="single_turn",
)

root_agent = Workflow(
    name="red_tag_incident_workflow",
    description="Evidence-first reasoning before the deterministic execution boundary.",
    edges=[
        (START, intake_agent),
        (intake_agent, investigator_agent),
        (investigator_agent, planner_agent),
        (planner_agent, executor_agent),
    ],
)

verification_root_agent = Workflow(
    name="red_tag_post_execution_verification",
    description="Verifies the durable action record after deterministic execution.",
    edges=[(START, verifier_agent)],
)
