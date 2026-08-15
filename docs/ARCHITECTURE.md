# Red Tag Architecture

```text
Public API (Cloud Run)
  -> Pub/Sub: red-tag-incident-created
  -> Private Worker (Cloud Run, authenticated push)
  -> Google ADK sequential workflow
  -> Safety policy + idempotent action executor
  -> Firestore incident, evidence, action, and idempotency records
```

## Agent workflow

1. Intake Agent normalizes severity, scope, symptoms, and missing facts.
2. Investigator Agent separates evidence from hypotheses and ranks causes.
3. Resolution Planner proposes the smallest reversible mitigation.
4. Action Executor applies policy and submits an idempotent action claim.
5. Closure Verifier requires action evidence before closing the incident.

The LLM never owns the execution guarantee. The deterministic execution boundary
owns policy, idempotency, and the action ledger.

## Reliability contract

- Pub/Sub delivery IDs are claimed before processing.
- Operational actions use a deterministic SHA-256 idempotency key.
- Firestore transactions provide the durable claim boundary.
- Duplicate delivery and duplicate action attempts create audit events.
- SEV1 and non-allowlisted actions stop at human approval.
- The worker returns a non-2xx response for malformed messages so Pub/Sub may
  retry and eventually route to a dead-letter topic.

## Local versus cloud mode

Local mode uses an in-memory repository and a deterministic workflow so safety
tests run without credentials or model cost. Cloud mode uses Firestore, Pub/Sub,
Vertex AI, and the ADK workflow. Both modes share the same models, policy, and
execution contract.
