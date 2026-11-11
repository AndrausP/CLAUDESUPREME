"""Curated organizational memory services."""

from __future__ import annotations

import re
from typing import Any

from .errors import ErrorCode, OrchestraError
from .models import MemoryStatus, MemoryType, new_id, utc_now
from .sanitize import digest, sanitize
from .storage import SQLiteStore


FORBIDDEN_CONTENT = re.compile(r"(-----BEGIN [A-Z ]+PRIVATE KEY-----|(?:api|access)[_-]?key\s*[:=]|password\s*[:=])", re.IGNORECASE)


class MemoryService:
    def __init__(self, store: SQLiteStore):
        self.store = store

    @staticmethod
    def canonical_key(title: str) -> str:
        normalized = re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")
        if not normalized:
            raise OrchestraError(ErrorCode.INVALID_SCHEMA, "memory title has no canonical characters")
        return normalized

    def propose(
        self,
        *,
        memory_type: MemoryType,
        scope: str,
        title: str,
        summary: str,
        content_ref: str,
        origin: dict[str, str],
        confidence: str = "medium",
        tags: list[str] | None = None,
        evidence_refs: list[str] | None = None,
    ) -> str:
        combined = "\n".join((title, summary, content_ref))
        if FORBIDDEN_CONTENT.search(combined):
            raise OrchestraError(ErrorCode.PERMISSION_DENIED, "memory appears to contain a secret")
        clean = sanitize({"title": title, "summary": summary, "content_ref": content_ref})
        content_sha = digest(clean)
        key = self.canonical_key(title)
        contradictions = self.store.find_memory(scope, key)
        relations: list[dict[str, str]] = []
        for existing in contradictions:
            if existing["canonical_key"] == key and existing["content_sha256"] != content_sha:
                relations.append({"type": "contradicts", "target": f"memory:{existing['memory_id']}"})
        memory_id = new_id()
        record: dict[str, Any] = {
            "memory_id": memory_id,
            "type": memory_type.value,
            "scope": scope,
            "canonical_key": key,
            "title": clean["title"],
            "summary": clean["summary"],
            "content_ref": clean["content_ref"],
            "origin": sanitize(origin),
            "created_at": utc_now(),
            "last_validated_at": None,
            "confidence": confidence,
            "status": MemoryStatus.PROPOSED.value,
            "tags": sorted(set(tags or [])),
            "relations": relations,
            "revision": 1,
            "evidence_refs": evidence_refs or [],
            "content_sha256": content_sha,
        }
        return self.store.insert_memory(record)

    def verify(self, memory_id: str, evidence_refs: list[str]) -> None:
        self.store.update_memory_status(memory_id, MemoryStatus.VERIFIED, evidence_refs)

    def invalidate(self, memory_id: str, status: MemoryStatus, evidence_refs: list[str] | None = None) -> None:
        if status not in {MemoryStatus.OUTDATED, MemoryStatus.SUPERSEDED, MemoryStatus.REJECTED}:
            raise OrchestraError(ErrorCode.INVALID_TRANSITION, f"cannot invalidate memory as {status.value}")
        self.store.update_memory_status(memory_id, status, evidence_refs or [])

    def search(self, scope: str, query: str, *, for_context: bool = True) -> list[dict[str, Any]]:
        return self.store.find_memory(scope, query, verified_only=for_context)

