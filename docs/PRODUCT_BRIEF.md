# Product Brief

## Working positioning

Red Tag is a safety-first background operations agent. It detects an operational
problem, gathers evidence, chooses the smallest reversible mitigation, executes
through an exactly-once safety boundary, verifies recovery, and leaves a complete
audit trail.

The original 24/7 SRE story is rejected: the entrant confirmed on 2026-08-15
that it is not a personal experience. It must not appear in submission material.

## Primary contest category

**The Taskmaster** is the primary category.

Why:

- the product is a complete asynchronous workflow;
- it performs a real action rather than returning chat text;
- the current architecture can be completed and polished before the deadline;
- safety, idempotency, and failure recovery directly support the architecture
  and production-readiness judging criteria.

The Fortified Enterprise Fleet is not the primary category for this submission.
It would require a broader enterprise agent catalog, long-term institutional
memory, cross-department governance, and additional platform services. Those
features would dilute the proof-of-action demo during the remaining build time.

## BYOF decision gate

Taskmaster judging explicitly rewards a unique personal friction. No final
product story may be locked until the entrant confirms it as truthful.

Strong current candidate: recurring Windows disk-pressure diagnosis and safe
cleanup. The workflow would:

- monitor free space and start in the background at a critical threshold;
- attribute growth across temporary files, package caches, Docker/WSL virtual
  disks, and uninstalled-application residue;
- distinguish regenerable cache from user data and required Docker volumes;
- execute only confirmed-safe cleanup actions through idempotency claims;
- require approval for user data, volumes, system files, or unknown targets;
- prove before, after, freed space, remaining large consumers, and every action.

This candidate reuses Red Tag's existing incident, evidence, policy, action
ledger, and duplicate-blocking architecture. It still requires explicit entrant
confirmation before becoming the submission story.

## Product twist

Most incident agents optimize reasoning. Red Tag treats execution correctness
as the differentiator: models may retry, workers may crash, and messages may be
delivered more than once, but a real mitigation is claimed once and evidenced.

## Four-minute proof story

1. A real background threshold creates an incident; no chat prompt is used.
2. ADK specialists produce evidence, hypothesis, reversible plan, and decision.
3. Red Tag performs a real, safe, measurable operational action.
4. A post-action probe proves recovery and Firestore records the full timeline.
5. The same event is delivered again; the UI shows `DUPLICATE BLOCKED` and
   proves the action count remains one.
6. A dangerous action is attempted and stops at the human approval boundary.

## Non-goals before submission

- a general-purpose chat assistant;
- dozens of superficial integrations;
- autonomous destructive actions;
- a broad enterprise platform without an undeniable end-to-end demo;
- features that cannot be shown inside the four-minute video.
