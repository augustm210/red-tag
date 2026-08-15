# Agent package

Implemented modules:

- `agent.py`: Google ADK graph workflow with five single-turn LLM nodes
- `workflow.py`: real ADK adapter and deterministic offline workflow
- `processor.py`: incident lifecycle orchestration and delivery deduplication
- `dispatch.py`: manual/local and Pub/Sub dispatch adapters
- `storage/`: in-memory and Firestore repositories
- `reliability/`: action policy, human approval gate, SHA-256 idempotency keys,
  and exactly-once action claims

The model produces analysis and plans. The reliability layer remains
deterministic and is the only component allowed to claim an operational action.
