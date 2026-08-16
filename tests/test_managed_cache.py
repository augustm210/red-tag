from pathlib import Path

import pytest

from red_tag_agent.models import Incident, IncidentCreate
from red_tag_agent.reliability.managed_cache import (
    ManagedCacheSafetyError,
    ManagedDirectoryCacheAdapter,
)


def incident() -> Incident:
    return Incident.from_create(
        IncidentCreate(
            title="Managed cache threshold crossed",
            description="Regenerable cache files crossed the configured safe threshold.",
            service="windows-disk",
            severity="SEV2",
            requested_action="clear_cache",
        )
    )


def test_managed_cache_deletes_only_cache_files(tmp_path: Path) -> None:
    root = tmp_path / "red-tag-demo"
    cache = ManagedDirectoryCacheAdapter.initialize(root)
    (cache / "nested").mkdir()
    (cache / "one.cache").write_bytes(b"a" * 17)
    (cache / "nested" / "two.cache").write_bytes(b"b" * 23)
    protected = root / "user-file.txt"
    protected.write_text("keep me", encoding="utf-8")

    evidence = ManagedDirectoryCacheAdapter(root).execute(incident(), "clear_cache")

    assert evidence["bytes_before"] == 40
    assert evidence["bytes_after"] == 0
    assert evidence["bytes_freed"] == 40
    assert evidence["files_deleted"] == 2
    assert protected.read_text(encoding="utf-8") == "keep me"
    assert evidence["marker_preserved"] is True


def test_unmarked_parent_is_blocked(tmp_path: Path) -> None:
    root = tmp_path / "red-tag-demo"
    ManagedDirectoryCacheAdapter.initialize(root)

    with pytest.raises(ManagedCacheSafetyError, match="Missing trusted marker"):
        ManagedDirectoryCacheAdapter(tmp_path).execute(incident(), "clear_cache")


def test_wrong_action_is_blocked(tmp_path: Path) -> None:
    root = tmp_path / "red-tag-demo"
    ManagedDirectoryCacheAdapter.initialize(root)

    with pytest.raises(ManagedCacheSafetyError, match="Unsupported local action"):
        ManagedDirectoryCacheAdapter(root).execute(incident(), "delete")
