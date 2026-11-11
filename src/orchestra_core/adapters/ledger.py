"""Unilateral Claude Ledger manifest/event adapter."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from ..models import utc_now
from ..sanitize import digest, sanitize
from ..storage import SQLiteStore


class LedgerAdapter:
    def __init__(self, store: SQLiteStore):
        self.store = store

    def write_manifest(
        self,
        destination: str | Path,
        *,
        departments: list[dict[str, Any]],
        agents: list[dict[str, Any]],
        skills: list[dict[str, Any]],
        checksums: dict[str, str] | None = None,
    ) -> dict[str, Any]:
        manifest = sanitize({
            "schema_version": "1.0.0",
            "organization_id": "orchestra-core-default",
            "protocol_version": "1.0.0",
            "package_version": "0.1.0",
            "generated_at": utc_now(),
            "departments": departments,
            "agents": agents,
            "skills": skills,
            "mcp_servers": [],
            "profiles": ["ECONOMY", "BALANCED", "QUALITY", "CRITICAL"],
            "policies": [{"id": "least-privilege", "version": "1.0.0"}],
            "dependencies": [],
            "integrations": {"claude_code": "available", "claude_ledger": "optional"},
            "checksums": checksums or {},
        })
        manifest["manifest_sha256"] = digest(manifest)
        path = Path(destination)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")
        return manifest

    def export_events(self, destination: str | Path) -> int:
        return self.store.export_events(destination)

