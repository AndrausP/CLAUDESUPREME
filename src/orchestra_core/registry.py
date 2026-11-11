"""Quarantined component registry with no-execution analysis."""

from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
import json
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

from .errors import ErrorCode, OrchestraError
from .storage import SQLiteStore


COMPONENT_TYPES = frozenset({"agent", "department", "skill", "mcp", "command", "hook", "validator", "workflow", "storage-provider"})
SCRIPT_SUFFIXES = frozenset({".ps1", ".sh", ".bat", ".cmd", ".exe", ".dll", ".py", ".js", ".mjs", ".cjs"})


@dataclass(frozen=True, slots=True)
class AnalysisReport:
    checksum: str
    files: int
    bytes: int
    executable_candidates: tuple[str, ...]
    warnings: tuple[str, ...]


class RegistryService:
    def __init__(self, store: SQLiteStore):
        self.store = store

    @staticmethod
    def validate_origin(origin: str) -> None:
        parsed = urlparse(origin)
        if parsed.scheme and parsed.scheme != "https":
            raise OrchestraError(ErrorCode.UNSAFE_EXTENSION, "external components require HTTPS", details={"scheme": parsed.scheme})
        if parsed.scheme == "https" and not parsed.netloc:
            raise OrchestraError(ErrorCode.UNSAFE_EXTENSION, "invalid HTTPS origin")

    @staticmethod
    def analyze(path: str | Path, *, max_files: int = 2_000, max_bytes: int = 50_000_000) -> AnalysisReport:
        root = Path(path).resolve()
        if not root.exists():
            raise OrchestraError(ErrorCode.NOT_FOUND, f"component path not found: {root.name}")
        candidates: list[str] = []
        warnings: list[str] = []
        total = 0
        count = 0
        hasher = sha256()
        files = [root] if root.is_file() else sorted((item for item in root.rglob("*") if item.is_file()), key=lambda p: p.as_posix())
        for item in files:
            if item.is_symlink():
                raise OrchestraError(ErrorCode.UNSAFE_EXTENSION, "symlinks are not allowed in quarantined components")
            count += 1
            if count > max_files:
                raise OrchestraError(ErrorCode.UNSAFE_EXTENSION, "component exceeds file limit")
            data = item.read_bytes()
            total += len(data)
            if total > max_bytes:
                raise OrchestraError(ErrorCode.UNSAFE_EXTENSION, "component exceeds size limit")
            relative = item.name if root.is_file() else item.relative_to(root).as_posix()
            hasher.update(relative.encode("utf-8"))
            hasher.update(b"\0")
            hasher.update(data)
            if item.suffix.lower() in SCRIPT_SUFFIXES:
                candidates.append(relative)
        if candidates:
            warnings.append("component contains executable/script candidates; analysis did not execute them")
        return AnalysisReport(hasher.hexdigest(), count, total, tuple(candidates), tuple(warnings))

    def register(
        self,
        *,
        component_id: str,
        version: str,
        component_type: str,
        origin_kind: str,
        origin_uri: str,
        path: str | Path,
        description: str,
        permissions: dict[str, Any] | None = None,
        dependencies: list[str] | None = None,
        compatibility: dict[str, Any] | None = None,
    ) -> AnalysisReport:
        if component_type not in COMPONENT_TYPES:
            raise OrchestraError(ErrorCode.INVALID_SCHEMA, f"unknown component type: {component_type}")
        if origin_kind != "local":
            self.validate_origin(origin_uri)
        report = self.analyze(path)
        self.store.upsert_component({
            "component_id": component_id,
            "version": version,
            "type": component_type,
            "origin": {"kind": origin_kind, "uri": origin_uri},
            "description": description,
            "permissions": permissions or {"tools": [], "network": False, "write_scopes": []},
            "dependencies": dependencies or [],
            "compatibility": compatibility or {},
            "status": "quarantined" if origin_kind != "local" else "disabled",
            "checksum": report.checksum,
            "configuration_ref": None,
        })
        return report

    def set_status(self, component_id: str, status: str, *, expected_checksum: str, external_confirmation: bool) -> None:
        allowed = {"quarantined", "disabled", "enabled", "incompatible", "failed", "removed"}
        if status not in allowed:
            raise OrchestraError(ErrorCode.INVALID_SCHEMA, f"invalid component status: {status}")
        current = self.store.get_component(component_id)
        if current["checksum"] != expected_checksum:
            raise OrchestraError(ErrorCode.CHECKSUM_MISMATCH, "component checksum changed")
        if status in {"enabled", "removed"} and not external_confirmation:
            raise OrchestraError(ErrorCode.PERMISSION_DENIED, f"{status} requires external confirmation")
        current["status"] = status
        self.store.upsert_component(current)

    def export_record(self, component_id: str, destination: str | Path) -> None:
        record = self.store.get_component(component_id)
        record.pop("updated_at", None)
        record["schema_version"] = "1.0.0"
        record["checksum"] = {"algorithm": "sha256", "value": record["checksum"]}
        Path(destination).write_text(json.dumps(record, indent=2, ensure_ascii=False), encoding="utf-8")

