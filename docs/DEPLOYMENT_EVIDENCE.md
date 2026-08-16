# Deployment Evidence

Verified 2026-08-16 against project `red-tag-agentic-2026-0815`.

## Live infrastructure

- Billing: enabled.
- Vertex AI: `gemini-3.6-flash` returned `RED_TAG_VERTEX_OK` through the
  `global` endpoint using Application Default Credentials.
- Google ADK: one live run returned all five expected authors: intake,
  investigator, resolution planner, action executor, and closure verifier.
- Cloud Build: build `557f1aa4-6529-4ad9-93df-59b97329c370` completed with
  status `SUCCESS`.
- Judge Console build: `bdd8b5d9-7b42-49a6-8574-e5f42115ebd9` completed with
  status `SUCCESS`.
- Post-execution verifier build: `0749182b-4a68-4d34-9ad9-076e3f2129ae`
  completed with status `SUCCESS`; Cloud Run revisions `red-tag-api-00003-zr4`
  and `red-tag-worker-00003-pvc` serve 100% of traffic.
- Public API: `https://red-tag-api-ododbqusqq-uc.a.run.app`.
- Private worker: `https://red-tag-worker-ododbqusqq-uc.a.run.app`.
- Firestore: `(default)`, Native mode, `us-central1`, free tier.
- Pub/Sub: authenticated OIDC push subscription `red-tag-worker-push` with
  dead-letter topic `red-tag-dead-letter`.
- Browser proof: the public Judge Console completed with five displayed stages
  and `REPLAY DUPLICATE_DELIVERY_BLOCKED / ACTION COUNT REMAINS 1`.
- Browser layout proof: 1440 px viewport had no horizontal overflow; all five
  full evidence payloads remained collapsed by default.

## End-to-end proof

Incident `b8261d60-3ff2-43b4-ac78-015b33f33f58` was created through the public
API and dispatched as Pub/Sub message `21026683801040272`.

Observed terminal state:

```json
{
  "status": "closed",
  "revision": 9,
  "events": 8,
  "actions": 1,
  "action_status": "completed"
}
```

The same delivery ID was then submitted again to the authenticated private
worker. The result was:

```json
{
  "outcome": "duplicate_delivery_blocked",
  "status": "closed",
  "action_count": 1,
  "duplicate_events": 1
}
```

## Honest limitation

The cloud action boundary intentionally uses the non-mutating safe demo adapter;
a multi-tenant public Cloud Run service must not mutate a judge's computer. The
separate Windows terminal proof now uses the same policy, processor, and
idempotency contract with the real managed-directory adapter.

Verified local run on 2026-08-16:

- threshold: 32 MiB; measured cache: 64 MiB;
- 64 files and 67,108,864 bytes removed;
- post-action managed bytes: 0;
- protected user-evidence file and safety marker preserved;
- unmarked parent target rejected;
- duplicate delivery outcome: `duplicate_delivery_blocked`;
- final action count: 1.

Raw evidence: [`artifacts/local-executor-proof.json`](../artifacts/local-executor-proof.json).
