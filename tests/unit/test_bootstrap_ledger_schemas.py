from __future__ import annotations

import json
from pathlib import Path
import tempfile
import unittest

from orchestra_core.adapters.agent_sdk import AgentSDKAdapter
from orchestra_core.adapters.ledger import LedgerAdapter
from orchestra_core.bootstrap import Bootstrapper


class BootstrapTests(unittest.TestCase):
    def test_bootstrap_is_idempotent_and_ledger_is_optional(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            first, first_store = Bootstrapper(root).run()
            first_store.close()
            second, second_store = Bootstrapper(root).run()
            self.assertEqual(first.project_id, second.project_id)
            adapter = LedgerAdapter(second_store)
            manifest = adapter.write_manifest(root / "manifest.json", departments=[], agents=[], skills=[])
            self.assertEqual("optional", manifest["integrations"]["claude_ledger"])
            self.assertTrue((root / "manifest.json").exists())
            second_store.close()

    def test_agent_sdk_adapter_reports_unavailability_without_credentials(self) -> None:
        status = AgentSDKAdapter().availability()
        self.assertIsInstance(status.available, bool)
        self.assertTrue(status.reason)


class SchemaTests(unittest.TestCase):
    def test_all_public_schemas_are_valid_json_with_2020_12_marker(self) -> None:
        schema_dir = Path(__file__).resolve().parents[2] / "schemas"
        schemas = list(schema_dir.glob("*.schema.json"))
        self.assertGreaterEqual(len(schemas), 12)
        for path in schemas:
            payload = json.loads(path.read_text(encoding="utf-8"))
            self.assertEqual("https://json-schema.org/draft/2020-12/schema", payload["$schema"], path.name)

    def test_profiles_parse_and_keep_safety_always(self) -> None:
        profile_dir = Path(__file__).resolve().parents[2] / "config" / "profiles"
        profiles = {json.loads(path.read_text(encoding="utf-8"))["profile"] for path in profile_dir.glob("*.json")}
        self.assertEqual({"ECONOMY", "BALANCED", "QUALITY", "CRITICAL"}, profiles)
        for path in profile_dir.glob("*.json"):
            self.assertEqual("always", json.loads(path.read_text(encoding="utf-8"))["enforcement"]["safety_minimums"])


if __name__ == "__main__":
    unittest.main()

