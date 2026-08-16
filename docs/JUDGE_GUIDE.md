# Judge Guide

## Fastest path

1. Open the [public Judge Console](https://red-tag-api-ododbqusqq-uc.a.run.app).
2. Press **RUN CLOUD PIPELINE**.
3. Wait for `PROOF COMPLETE` and inspect the five evidence stages.
4. Confirm the red replay block reads `ACTION COUNT REMAINS 1`.

No account, payment, API key, or test credential is required.

## What the public proof demonstrates

- Gemini 3.6 Flash through Vertex AI's global endpoint;
- five Google ADK specialists;
- a public Cloud Run API and private Cloud Run worker;
- authenticated Pub/Sub delivery and Firestore persistence;
- a deterministic policy and transactional idempotency boundary;
- duplicate delivery rejection after a completed action.

The public deployment uses a non-mutating adapter because a shared web demo
must not modify a judge's computer.

## Real action proof on Windows

From an editable checkout with Python 3.11+:

```powershell
python -m venv .venv
.\.venv\Scripts\python -m pip install -e ".[dev]"
.\scripts\run_windows_proof.ps1
```

The script creates a 64 MiB regenerable cache inside `.red-tag-demo`, measures
the threshold crossing, processes the incident, deletes only marked cache files,
verifies zero managed bytes remain, and replays the same delivery. The parent
directory safety probe must be blocked and the protected evidence file must
survive.

## Reliability tests

```powershell
.\.venv\Scripts\python -m ruff check .
.\.venv\Scripts\python -m pytest
```

The suite covers API lifecycle, SEV1 approval, unknown/high-risk actions,
duplicate delivery, duplicate action, real cache deletion, unmarked-parent
rejection, and unsupported local actions.

## Evidence index

- [`DEPLOYMENT_EVIDENCE.md`](DEPLOYMENT_EVIDENCE.md)
- [`local-executor-proof.json`](../artifacts/local-executor-proof.json)
- [`judge-console-proof-v2.png`](../artifacts/judge-console-proof-v2.png)
- [`architecture.svg`](../artifacts/architecture.svg)
- [`ARCHITECTURE.md`](ARCHITECTURE.md)
