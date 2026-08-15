# Red Tag

Red Tag is a safety-first incident response agent for Google Cloud. It turns an
incident report into an evidence-backed investigation, a constrained action
plan, an idempotent execution, and a verified closure record.

The project is intentionally built around one hard reliability promise:

> A retried event may repeat the reasoning, but it must never repeat an
> operational action.

## Current vertical slice

- FastAPI incident API
- Google ADK five-stage workflow definition
- deterministic local workflow for offline development and tests
- Firestore-ready incident and audit repository
- Pub/Sub-ready dispatcher and authenticated push endpoint
- action allowlist, human-approval gate, action ledger, and idempotency keys
- duplicate delivery and duplicate action tests
- Cloud Run container

## Quick start

```powershell
python -m venv .venv
.\.venv\Scripts\python -m pip install -e ".[dev]"
Copy-Item .env.example .env
.\.venv\Scripts\python -m uvicorn services.api.main:app --reload
```

Open `http://127.0.0.1:8000/docs`, create an incident, and process it with the
returned incident ID.

```powershell
$incident = Invoke-RestMethod -Method Post `
  -Uri http://127.0.0.1:8000/v1/incidents `
  -ContentType application/json `
  -Body '{"title":"Checkout latency spike","description":"p95 latency is 4.8s after release 2026.08.15","service":"checkout","severity":"SEV2","requested_action":"rollback"}'

Invoke-RestMethod -Method Post `
  -Uri "http://127.0.0.1:8000/v1/incidents/$($incident.id)/process" `
  -ContentType application/json `
  -Body '{"delivery_id":"demo-delivery-001"}'
```

The default `local` mode is deterministic and does not call a model. For a real
ADK/Gemini run, configure the Google Cloud variables in `.env` and set
`RED_TAG_AGENT_MODE=adk`.

## Tests

```powershell
.\.venv\Scripts\python -m pytest
```

## Google Cloud deployment

The deployment script is deliberately not run until a dedicated project and
billing choice are confirmed.

```powershell
.\scripts\deploy_gcp.ps1 -ProjectId YOUR_PROJECT_ID -Region us-central1
```

See [architecture](docs/ARCHITECTURE.md) and the
[deployment checklist](docs/DEPLOY_CHECKLIST.md). Competition delivery is
governed by the [championship scorecard](docs/CHAMPIONSHIP_SCORECARD.md) and
[product brief](docs/PRODUCT_BRIEF.md).
