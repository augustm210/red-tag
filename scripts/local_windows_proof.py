from __future__ import annotations

import argparse
import json
from pathlib import Path

from red_tag_agent.models import Incident, IncidentCreate
from red_tag_agent.processor import IncidentProcessor
from red_tag_agent.reliability.executor import SafeActionExecutor
from red_tag_agent.reliability.managed_cache import (
    ManagedCacheSafetyError,
    ManagedDirectoryCacheAdapter,
)
from red_tag_agent.reliability.policy import ActionPolicy
from red_tag_agent.storage.memory import InMemoryIncidentRepository
from red_tag_agent.workflow import LocalIncidentWorkflow


def seed(cache: Path, megabytes: int) -> list[Path]:
    cache.mkdir(parents=True, exist_ok=True)
    paths: list[Path] = []
    chunk = bytes([0xA5]) * (1024 * 1024)
    for index in range(megabytes):
        path = cache / f"regenerable-{index:03d}.cache"
        path.write_bytes(chunk)
        paths.append(path)
    return paths


def run(root: Path, threshold_mb: int, seed_mb: int) -> dict[str, object]:
    cache = ManagedDirectoryCacheAdapter.initialize(root)
    protected = root / "DO_NOT_DELETE-user-evidence.txt"
    protected.write_text(
        "Protected user evidence. Red Tag must preserve this file.\n",
        encoding="utf-8",
    )
    seed(cache, seed_mb)
    adapter = ManagedDirectoryCacheAdapter(root)
    measured = adapter.measure()
    threshold = threshold_mb * 1024 * 1024
    if measured < threshold:
        return {
            "outcome": "threshold_not_crossed",
            "managed_bytes": measured,
            "threshold_bytes": threshold,
        }

    repository = InMemoryIncidentRepository()
    incident = repository.create(
        Incident.from_create(
            IncidentCreate(
                title="Managed Windows cache threshold crossed",
                description=(
                    "A background measurement found regenerable files above the configured "
                    "managed-directory threshold."
                ),
                service="windows-disk",
                severity="SEV2",
                requested_action="clear_cache",
                signals={
                    "source": "windows-threshold-monitor",
                    "managed_cache_bytes": measured,
                    "threshold_bytes": threshold,
                },
            )
        )
    )
    processor = IncidentProcessor(
        repository,
        LocalIncidentWorkflow(),
        SafeActionExecutor(repository, ActionPolicy(), adapter),
    )
    first = processor.process(incident.id, "windows-proof-delivery-001")
    duplicate = processor.process(incident.id, "windows-proof-delivery-001")
    stored = repository.get(incident.id)
    if stored is None:
        raise RuntimeError("Incident disappeared from the repository")

    try:
        ManagedDirectoryCacheAdapter(root.parent).measure()
        unsafe_probe = "unexpectedly_allowed"
    except ManagedCacheSafetyError as exc:
        unsafe_probe = f"blocked: {exc}"

    action = stored.actions[0]
    proof = {
        "outcome": first.outcome,
        "incident_id": incident.id,
        "trigger": incident.signals,
        "action": action.model_dump(mode="json"),
        "duplicate_delivery": {
            "outcome": duplicate.outcome,
            "action_count": len(stored.actions),
        },
        "unsafe_parent_probe": unsafe_probe,
        "protected_file_exists": protected.is_file(),
        "audit_event_types": [event.event_type for event in stored.events],
    }
    return proof


def main() -> None:
    parser = argparse.ArgumentParser(description="Run Red Tag's safe Windows cleanup proof")
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--threshold-mb", type=int, default=32)
    parser.add_argument("--seed-mb", type=int, default=64)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    proof = run(args.root, args.threshold_mb, args.seed_mb)
    rendered = json.dumps(proof, indent=2, ensure_ascii=False)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered + "\n", encoding="utf-8")
    print(rendered)


if __name__ == "__main__":
    main()
