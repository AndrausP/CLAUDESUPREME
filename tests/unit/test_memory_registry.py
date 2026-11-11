from __future__ import annotations

import json
from pathlib import Path
import tempfile
import unittest

from orchestra_core.errors import ErrorCode, OrchestraError
from orchestra_core.memory import MemoryService
from orchestra_core.models import MemoryStatus, MemoryType, new_id
from orchestra_core.registry import RegistryService
from orchestra_core.storage import SQLiteStore


class ServiceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.store = SQLiteStore(self.root / "state.db")
        self.project_id = new_id()
        self.store.ensure_project(self.project_id, "test")

    def tearDown(self) -> None:
        self.store.close()
        self.temp.cleanup()

    def test_memory_requires_evidence_to_enter_context(self) -> None:
        service = MemoryService(self.store)
        memory_id = service.propose(
            memory_type=MemoryType.PROJECT, scope=f"project:{self.project_id}", title="Use SQLite",
            summary="SQLite is authoritative", content_ref="docs/architecture.md#sqlite", origin={"type": "task", "id": new_id()},
        )
        self.assertEqual([], service.search(f"project:{self.project_id}", "SQLite", for_context=True))
        with self.assertRaises(OrchestraError):
            service.verify(memory_id, [])
        service.verify(memory_id, ["evidence:test"])
        self.assertEqual(1, len(service.search(f"project:{self.project_id}", "SQLite", for_context=True)))
        service.invalidate(memory_id, MemoryStatus.OUTDATED, ["evidence:newer"])
        self.assertEqual([], service.search(f"project:{self.project_id}", "SQLite", for_context=True))

    def test_memory_duplicate_and_secret_detection(self) -> None:
        service = MemoryService(self.store)
        kwargs = dict(memory_type=MemoryType.ORGANIZATIONAL, scope="org:default", title="Rule", summary="Safe", content_ref="docs/rule", origin={"type": "task", "id": new_id()})
        service.propose(**kwargs)
        with self.assertRaises(OrchestraError) as duplicate:
            service.propose(**kwargs)
        self.assertEqual(ErrorCode.INVALID_SCHEMA, duplicate.exception.code)
        with self.assertRaises(OrchestraError) as secret:
            service.propose(memory_type=MemoryType.PROJECT, scope="x", title="credential", summary="api_key=abc", content_ref="x", origin={"type": "task", "id": new_id()})
        self.assertEqual(ErrorCode.PERMISSION_DENIED, secret.exception.code)

    def test_registry_never_executes_and_requires_external_confirmation(self) -> None:
        component = self.root / "component"
        component.mkdir()
        marker = self.root / "executed.txt"
        (component / "danger.py").write_text(f"from pathlib import Path\nPath({str(marker)!r}).write_text('bad')\n", encoding="utf-8")
        registry = RegistryService(self.store)
        report = registry.register(
            component_id="skill:test", version="1.0.0", component_type="skill", origin_kind="git",
            origin_uri="https://example.com/repo.git", path=component, description="test",
        )
        self.assertFalse(marker.exists())
        self.assertIn("danger.py", report.executable_candidates)
        with self.assertRaises(OrchestraError) as denied:
            registry.set_status("skill:test", "enabled", expected_checksum=report.checksum, external_confirmation=False)
        self.assertEqual(ErrorCode.PERMISSION_DENIED, denied.exception.code)
        registry.set_status("skill:test", "enabled", expected_checksum=report.checksum, external_confirmation=True)
        self.assertEqual("enabled", self.store.get_component("skill:test")["status"])

    def test_registry_rejects_non_https_external_origin(self) -> None:
        registry = RegistryService(self.store)
        with self.assertRaises(OrchestraError) as raised:
            registry.register(component_id="skill:x", version="1", component_type="skill", origin_kind="git", origin_uri="ssh://example/repo", path=self.root, description="x")
        self.assertEqual(ErrorCode.UNSAFE_EXTENSION, raised.exception.code)


if __name__ == "__main__":
    unittest.main()

