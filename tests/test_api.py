from fastapi.testclient import TestClient

from services.api.dependencies import get_dispatcher, get_processor, get_repository
from services.api.main import app


def reset_dependencies() -> None:
    get_dispatcher.cache_clear()
    get_processor.cache_clear()
    get_repository.cache_clear()


def test_incident_closes_and_duplicate_delivery_is_blocked() -> None:
    reset_dependencies()
    client = TestClient(app)
    created = client.post(
        "/v1/incidents",
        json={
            "title": "Checkout latency spike",
            "description": "Latency increased immediately after the latest release.",
            "service": "checkout",
            "severity": "SEV2",
            "requested_action": "rollback",
            "signals": {"p95_ms": 4800},
        },
    )
    assert created.status_code == 201
    incident_id = created.json()["id"]

    first = client.post(
        f"/v1/incidents/{incident_id}/process",
        json={"delivery_id": "delivery-001"},
    )
    assert first.status_code == 200
    assert first.json()["outcome"] == "closed"
    assert first.json()["action"]["status"] == "completed"

    duplicate = client.post(
        f"/v1/incidents/{incident_id}/process",
        json={"delivery_id": "delivery-001"},
    )
    assert duplicate.status_code == 200
    assert duplicate.json()["outcome"] == "duplicate_delivery_blocked"

    stored = client.get(f"/v1/incidents/{incident_id}").json()
    assert len(stored["actions"]) == 1
    assert any(event["event_type"] == "duplicate_delivery_blocked" for event in stored["events"])


def test_sev1_requires_human_approval() -> None:
    reset_dependencies()
    client = TestClient(app)
    created = client.post(
        "/v1/incidents",
        json={
            "title": "Production database saturation",
            "description": "Connections are exhausted and writes are timing out.",
            "service": "payments-db",
            "severity": "SEV1",
            "requested_action": "restart",
        },
    )
    incident_id = created.json()["id"]
    result = client.post(
        f"/v1/incidents/{incident_id}/process",
        json={"delivery_id": "delivery-sev1"},
    )
    assert result.status_code == 200
    assert result.json()["outcome"] == "human_approval_required"
    assert result.json()["status"] == "awaiting_approval"


def test_unknown_action_is_never_executed() -> None:
    reset_dependencies()
    client = TestClient(app)
    created = client.post(
        "/v1/incidents",
        json={
            "title": "Untrusted remediation request",
            "description": "A report asks the system to delete production data.",
            "service": "customer-data",
            "severity": "SEV2",
            "requested_action": "drop_database",
        },
    )
    incident_id = created.json()["id"]
    result = client.post(
        f"/v1/incidents/{incident_id}/process",
        json={"delivery_id": "delivery-danger"},
    )
    assert result.json()["outcome"] == "human_approval_required"
    assert result.json()["action"]["status"] == "awaiting_approval"
