# Product Brief

## Working positioning

Red Tag is an autonomous incident response operator for solo founders and small
engineering teams that cannot staff a 24/7 SRE rotation.

It detects an incident, gathers evidence, chooses the smallest reversible
mitigation, executes through an exactly-once safety boundary, verifies recovery,
and leaves a complete audit trail.

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

## User and friction

Primary user: a solo founder or a small team member who is responsible for an
online service but cannot continuously watch alerts.

Friction:

- incidents arrive while the operator is asleep or focused elsewhere;
- diagnosis is spread across alerts, deploy history, and service telemetry;
- retrying automation can repeat destructive or costly actions;
- existing copilots often recommend steps but do not safely execute them;
- after recovery, the operator lacks a trustworthy timeline of what happened.

The submission must not claim that this is the entrant's personal experience
until the entrant confirms a truthful first-hand story.

## Product twist

Most incident agents optimize reasoning. Red Tag treats execution correctness
as the differentiator: models may retry, workers may crash, and messages may be
delivered more than once, but a real mitigation is claimed once and evidenced.

## Four-minute proof story

1. A deployment causes checkout latency while the operator is unavailable.
2. A real background event creates an incident; no chat prompt is used.
3. ADK specialists produce evidence, hypothesis, reversible plan, and decision.
4. Red Tag performs a real safe rollback or Cloud Run revision traffic change.
5. Health checks prove recovery and Firestore records the action and timeline.
6. The same Pub/Sub message is delivered again; the UI shows `DUPLICATE BLOCKED`
   and proves the action count remains one.
7. A dangerous action is attempted and stops at the human approval boundary.

## Non-goals before submission

- a general-purpose chat assistant;
- dozens of superficial integrations;
- autonomous destructive actions;
- a broad enterprise platform without an undeniable end-to-end demo;
- features that cannot be shown inside the four-minute video.
