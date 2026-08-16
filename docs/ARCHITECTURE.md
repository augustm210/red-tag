# Red Tag Architecture

```text
Public API (Cloud Run)
  -> Pub/Sub: red-tag-incident-created
  -> Private Worker (Cloud Run, authenticated push)
  -> Google ADK sequential workflow
  -> Safety policy + idempotent action executor
  -> Firestore incident, evidence, action, and idempotency records

Windows threshold proof (local terminal)
  -> Marked sandbox measurement
  -> Shared incident processor + safety policy
  -> Managed-directory action adapter
  -> Byte-level before/after evidence
  -> Duplicate replay blocked by the shared action ledger
```

## Agent workflow

1. Intake Agent normalizes severity, scope, symptoms, and missing facts.
2. Investigator Agent separates evidence from hypotheses and ranks causes.
3. Resolution Planner proposes the smallest reversible mitigation.
4. Action Executor Agent reviews the plan and proposes an action; it cannot run it.
5. The deterministic safety boundary applies policy, claims the idempotency key,
   and records completion.
6. Closure Verifier runs after execution and receives the durable action record.

There are five Gemini/ADK specialists. The deterministic safety boundary between
the fourth and fifth specialists is deliberately not an LLM agent.

The LLM never owns the execution guarantee or claims success before evidence.
The deterministic execution boundary owns policy, idempotency, and the action
ledger; the final LLM node only interprets the post-execution record.

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

## Filesystem safety boundary

The local adapter accepts exactly one manifest:
`.red-tag-managed-cache.json` with schema `red-tag-managed-cache/v1`. It resolves
the marked root, requires a real `cache` child, refuses linked directories and
non-regular files, and verifies every resolved target stays below that child.
Files next to `cache` are evidence, not deletion candidates. The parent path is
probed during every proof run and must fail closed because it has no marker.
