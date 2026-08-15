# Cloud services

The first vertical slice packages API and worker routes in one container and
deploys it twice with different service roles:

- `red-tag-api`: public incident creation and read endpoints; publishes Pub/Sub
  messages.
- `red-tag-worker`: private authenticated Pub/Sub endpoint; runs the ADK
  workflow and safety-gated action executor.

`RED_TAG_SERVICE_ROLE` hides worker routes from the public deployment and API
routes from the private worker deployment. Pub/Sub failures are routed to the
`red-tag-dead-letter` topic for the next-stage dead-letter recorder.
