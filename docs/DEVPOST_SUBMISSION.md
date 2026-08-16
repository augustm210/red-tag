# Devpost Submission Draft

## Project name

Red Tag

## Tagline

When the disk turns red, the agent acts once.

## Inspiration

On the entrant's Windows machine, the system drive had only 19.97 GB free while
another drive had 927.86 GB free. Moving data was easy; knowing what an agent
could safely delete was not. Existing cleanup tools optimize for bytes removed,
but an autonomous agent also has to survive retries, worker crashes, and duplicate
messages without repeating a destructive action.

## What it does

Red Tag is a background operations agent for disk pressure. A real threshold
measurement creates an incident without a chat prompt. Five Google ADK agents
normalize the report, investigate evidence, choose the smallest reversible plan,
submit it to a deterministic safety boundary, and verify closure. The Windows
adapter deletes only files inside a signed managed-cache directory and records
before/after bytes. A replay of the same delivery is blocked and the action count
remains one.

## How we built it

The public control plane runs on Google Cloud Run. Pub/Sub sends authenticated
push messages to a private worker. Google ADK 2.7 orchestrates five specialists
using Gemini 3.6 Flash on Vertex AI's global endpoint. Firestore stores incidents,
audit events, actions, and transactional delivery/action claims. A deterministic
Python boundary owns the allowlist, approval rules, target validation, and
idempotency guarantee. The real Windows adapter shares that boundary with the
cloud demo.

## Challenges

The hardest problem was separating agent reasoning from execution correctness.
LLMs and message systems retry by design, so prompt instructions cannot provide
an exactly-once guarantee. We placed a durable SHA-256 action claim between the
planning and verification agents and made the adapter return machine-verifiable
evidence. We also designed the filesystem contract to fail closed on missing
markers, links, unknown files, or paths outside the managed child directory.

## Accomplishments

- Public one-click cloud proof with no credentials or payment.
- Five live Gemini/ADK evidence stages.
- Authenticated Cloud Run worker, Firestore audit trail, and Pub/Sub delivery.
- Real 64 MiB Windows cache action with 67,108,864 bytes verified as freed.
- Protected-file preservation and unmarked-parent rejection.
- Duplicate delivery leaves exactly one action in the ledger.
- Eight reliability and API tests plus static analysis.

## What we learned

Autonomous operations is less about generating a clever plan and more about
making the action boundary boring, inspectable, and impossible to repeat. The
best agent architecture lets models retry freely while deterministic code owns
permissions, claims, execution, and evidence.

## What's next

We will add signed remote-device enrollment, OpenTelemetry trace correlation,
configurable cache providers, and an approval inbox for targets outside the
autonomous allowlist. The same exactly-once boundary can then cover container
rollbacks and cloud resource remediation.

## Built with

Python, FastAPI, Google ADK, Gemini 3.6 Flash, Vertex AI, Cloud Run, Pub/Sub,
Firestore, Cloud Build, PowerShell, Docker.

## Links

- Live app: https://red-tag-api-ododbqusqq-uc.a.run.app
- Source: to be added after public repository creation
