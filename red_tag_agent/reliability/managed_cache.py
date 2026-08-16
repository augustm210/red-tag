from __future__ import annotations

import json
import os
import shutil
from pathlib import Path
from typing import Any

from red_tag_agent.models import Incident


class ManagedCacheSafetyError(RuntimeError):
    """Raised when a filesystem target does not satisfy the safety contract."""


class ManagedDirectoryCacheAdapter:
    """Deletes only regular files inside an explicitly marked cache directory."""

    MARKER = ".red-tag-managed-cache.json"
    SCHEMA = "red-tag-managed-cache/v1"

    def __init__(self, root: Path) -> None:
        self.root = root

    @classmethod
    def initialize(cls, root: Path) -> Path:
        resolved = root.resolve()
        resolved.mkdir(parents=True, exist_ok=True)
        cache = resolved / "cache"
        cache.mkdir(exist_ok=True)
        marker = resolved / cls.MARKER
        marker.write_text(
            json.dumps({"schema": cls.SCHEMA, "managed_subdirectory": "cache"}),
            encoding="utf-8",
        )
        return cache

    def execute(self, incident: Incident, action_name: str) -> dict[str, Any]:
        if action_name != "clear_cache":
            raise ManagedCacheSafetyError(f"Unsupported local action: {action_name}")
        root, cache = self._validate()
        before = self._measure(cache)
        disk_before = shutil.disk_usage(root).free
        deleted_files = 0

        for current, dirnames, filenames in os.walk(cache, topdown=True, followlinks=False):
            current_path = Path(current)
            safe_dirs: list[str] = []
            for dirname in dirnames:
                candidate = current_path / dirname
                if candidate.is_symlink():
                    raise ManagedCacheSafetyError(f"Refusing linked directory: {candidate}")
                safe_dirs.append(dirname)
            dirnames[:] = safe_dirs
            for filename in filenames:
                candidate = current_path / filename
                if candidate.is_symlink() or not candidate.is_file():
                    raise ManagedCacheSafetyError(f"Refusing non-regular file: {candidate}")
                resolved_candidate = candidate.resolve(strict=True)
                if not resolved_candidate.is_relative_to(cache):
                    raise ManagedCacheSafetyError(f"Target escaped managed cache: {candidate}")
                candidate.unlink()
                deleted_files += 1

        for current, dirnames, _ in os.walk(cache, topdown=False, followlinks=False):
            for dirname in dirnames:
                candidate = Path(current) / dirname
                if not candidate.is_symlink():
                    try:
                        candidate.rmdir()
                    except OSError:
                        pass

        after = self._measure(cache)
        disk_after = shutil.disk_usage(root).free
        return {
            "adapter": "managed_directory_windows",
            "verification_scope": "local_filesystem",
            "managed_root": str(root),
            "managed_cache": str(cache),
            "bytes_before": before,
            "bytes_after": after,
            "bytes_freed": before - after,
            "files_deleted": deleted_files,
            "volume_free_bytes_before": disk_before,
            "volume_free_bytes_after": disk_after,
            "marker_preserved": (root / self.MARKER).is_file(),
            "protected_files_preserved": sorted(
                str(item.relative_to(root))
                for item in root.iterdir()
                if item.name not in {self.MARKER, "cache"}
            ),
            "incident_id": incident.id,
        }

    def measure(self) -> int:
        _, cache = self._validate()
        return self._measure(cache)

    def _validate(self) -> tuple[Path, Path]:
        if not self.root.exists() or self.root.is_symlink():
            raise ManagedCacheSafetyError("Managed root must be an existing real directory")
        root = self.root.resolve(strict=True)
        marker = root / self.MARKER
        if not marker.is_file() or marker.is_symlink():
            raise ManagedCacheSafetyError(f"Missing trusted marker: {marker}")
        try:
            manifest = json.loads(marker.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise ManagedCacheSafetyError("Managed marker is unreadable or invalid") from exc
        if manifest != {"schema": self.SCHEMA, "managed_subdirectory": "cache"}:
            raise ManagedCacheSafetyError("Managed marker does not match the safety contract")
        cache = root / "cache"
        if not cache.exists() or cache.is_symlink():
            raise ManagedCacheSafetyError("Managed cache must be an existing real directory")
        cache = cache.resolve(strict=True)
        if cache.parent != root:
            raise ManagedCacheSafetyError("Managed cache escaped its marked root")
        return root, cache

    @staticmethod
    def _measure(cache: Path) -> int:
        total = 0
        for current, dirnames, filenames in os.walk(cache, topdown=True, followlinks=False):
            current_path = Path(current)
            dirnames[:] = [name for name in dirnames if not (current_path / name).is_symlink()]
            for filename in filenames:
                candidate = current_path / filename
                if candidate.is_symlink() or not candidate.is_file():
                    continue
                total += candidate.stat().st_size
        return total
