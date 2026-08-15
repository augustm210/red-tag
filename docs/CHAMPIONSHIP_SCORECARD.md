# Championship Scorecard

Source of truth: [All Things Agentic Hackathon official rules](https://allthingsagentichackathon.devpost.com/rules),
reviewed 2026-08-15.

Submission deadline: 2026-09-01 08:00 Asia/Shanghai.

This file is a release gate. A checked item must be backed by a test, deployed
artifact, public URL, trace, screenshot, or video timestamp. A README claim is
not evidence.

## Stage One: mandatory pass/fail

- [x] Project was created during the submission period.
- [x] Gemini 3.5 or newer selected (`gemini-3.6-flash`).
- [x] Google Agent Framework selected (Google ADK 2.7 Workflow).
- [x] Google Cloud infrastructure designed (Cloud Run, Firestore, Pub/Sub).
- [x] English-language application path exists.
- [ ] Public, reproducible GitHub repository.
- [ ] Public working deployment that judges can use without payment.
- [ ] Four-minute-or-shorter English demonstration video.
- [ ] Testing instructions and any required test credentials.
- [ ] All third-party assets, data, and libraries have documented licenses.
- [ ] Pre-existing work disclosure completed.

Any unchecked Stage One item blocks submission.

## Primary category: The Taskmaster

Red Tag will compete as a complete background workflow, not a chat interface.
Its task is to take an incident from detection to evidence-backed, safe,
reversible remediation and verified closure.

Category proof requirements:

- [ ] A real incident source triggers Red Tag without a chat prompt.
- [ ] At least one multi-step incident closes without human intervention.
- [ ] The user friction and personal origin are truthful and specific.
- [ ] The workflow sends results to an external operational destination.
- [ ] The demo proves the system acts instead of merely recommending an action.

## Innovation and operational utility — 40%

Winning claim:

> Autonomous remediation is dangerous when retries repeat real actions. Red Tag
> combines multi-agent investigation with a deterministic exactly-once safety
> boundary, so a background agent can act without turning a retry into a second
> outage.

Evidence gates:

- [x] Five specialized stages with explicit responsibilities.
- [x] Safe action allowlist and SEV1 approval gate.
- [x] Duplicate Pub/Sub delivery detection.
- [x] Deterministic action idempotency key.
- [x] Duplicate action blocking test.
- [ ] Real reversible Google Cloud action adapter.
- [ ] Before/after service-health verification.
- [ ] Quantified baseline versus Red Tag: time-to-triage and time-to-mitigation.
- [ ] Failure-injection demo: timeout, retry, duplicate delivery, and worker crash.
- [ ] User validation showing the workflow solves credible operational pain.

Target score: 5/5.

## Architectural discipline and tech stack — 30%

- [x] API, dispatch, workflow, repository, policy, and executor are decoupled.
- [x] Agent reasoning is separated from deterministic execution safety.
- [x] API and worker have distinct Cloud Run roles.
- [x] Firestore transaction owns the durable action claim.
- [x] Authenticated Pub/Sub push is represented in deployment automation.
- [x] Dead-letter topic is represented in deployment automation.
- [ ] Cloud deployment passes from a clean checkout.
- [ ] Least-privilege IAM is verified in the deployed project.
- [ ] Dead-letter recorder and replay workflow are implemented.
- [ ] Agent timeout, malformed output, loop, and hallucination recovery are tested.
- [ ] OpenTelemetry traces correlate API, Pub/Sub, ADK nodes, and action ledger.
- [ ] Secret and PII handling are documented and tested.
- [ ] Load and concurrency tests prove one action under parallel duplicate delivery.
- [ ] Cloud costs and maximum resource limits are documented.

Target score: 5/5.

## Demo and production readiness — 30%

- [ ] Public incident command UI is polished and usable on first visit.
- [ ] Public API and judge test path remain online through 2026-10-02.
- [ ] Four-minute video has an unedited proof-of-action sequence.
- [ ] Video visibly proves Gemini/ADK and Google Cloud runtime use.
- [ ] Video visibly proves Firestore updates and duplicate-action blocking.
- [ ] Public GitHub has a clean architecture diagram and one-command setup.
- [ ] README includes a 60-second quick start and judge test script.
- [ ] Demo has a rehearsed fallback recording and seeded incident data.
- [ ] All claims in narration map to visible evidence.

Target score: 5/5.

## Bonus contribution plan — maximum +1.0

- [ ] +0.2 public engineering article or video with required contest disclosure.
- [ ] +0.2 public social post with `#AllThingsAgenticHackathon`.
- [ ] +0.2 additional Google AI model integration #1.
- [ ] +0.2 additional Google AI model integration #2.
- [ ] +0.2 additional Google AI model integration #3.

Additional models must materially improve the product and appear in runtime
evidence. Decorative API calls do not meet the Red Tag quality bar.

## Submission safety

- [ ] Devpost registration and team membership are correct.
- [ ] Entrant eligibility is confirmed.
- [ ] Winner-notification email is monitored daily through 2026-10-10.
- [ ] Identity, tax, and prize paperwork can be returned within two days.
- [ ] Final submission is completed at least 24 hours before the deadline.
