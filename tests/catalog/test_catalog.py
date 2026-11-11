from __future__ import annotations

import hashlib
import json
from pathlib import Path
import re
import sys
import unittest


ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from orchestra_core.cli import _normalize_global_options, build_parser


def load_json(relative: str) -> dict:
    return json.loads((ROOT / relative).read_text(encoding="utf-8"))


def frontmatter(path: Path) -> dict[str, str]:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        raise AssertionError(f"frontmatter ausente: {path}")
    block = text.split("---\n", 2)[1]
    result: dict[str, str] = {}
    for line in block.splitlines():
        if line and not line.startswith(" ") and ":" in line:
            key, value = line.split(":", 1)
            result[key.strip()] = value.strip()
    return result


class CatalogTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.agents = load_json("catalogs/agents.json")
        cls.skills = load_json("catalogs/skills.json")

    def test_exact_organization_shape(self) -> None:
        self.assertEqual(7, len(self.agents["departments"]))
        self.assertEqual(36, len(self.agents["agents"]))
        self.assertEqual([5] * 7, sorted(len(item["agents"]) for item in self.agents["departments"]))
        self.assertEqual(1, sum(item["id"] == "central-orchestrator" for item in self.agents["agents"]))

    def test_agent_ids_and_responsibilities_are_unique(self) -> None:
        items = self.agents["agents"]
        self.assertEqual(len(items), len({item["id"] for item in items}))
        self.assertEqual(len(items), len({item["responsibility"] for item in items}))
        for item in items:
            self.assertRegex(item["id"], r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
            self.assertLessEqual(len(frontmatter(ROOT / item["ref"])["description"]), 180)

    def test_agent_frontmatter_uses_plugin_supported_fields(self) -> None:
        allowed = {"name", "description", "model", "effort", "maxTurns", "tools", "disallowedTools", "skills", "memory", "background", "omitClaudeMd", "isolation", "color", "experimental"}
        for item in self.agents["agents"]:
            meta = frontmatter(ROOT / item["ref"])
            self.assertTrue({"name", "description"}.issubset(meta))
            self.assertFalse(set(meta) - allowed, f"campos não suportados em {item['id']}")
            self.assertNotIn("permissionMode", meta)
            self.assertNotIn("hooks", meta)
            self.assertNotIn("mcpServers", meta)

    def test_exact_primary_skills_and_agent_references(self) -> None:
        primary = self.skills["primary"]
        self.assertEqual(36, len(primary))
        self.assertEqual(36, len({item["id"] for item in primary}))
        available = {item["id"] for item in primary}
        self.assertEqual(available, {item["primary_skill"] for item in self.agents["agents"]})

    def test_materialized_checksums(self) -> None:
        entries = self.agents["agents"] + self.skills["primary"] + self.skills["shared"] + self.skills["commands"]
        for item in entries:
            content = (ROOT / item["ref"]).read_text(encoding="utf-8")
            digest = hashlib.sha256(content.encode("utf-8")).hexdigest()
            self.assertEqual(item["sha256"], digest, item["ref"])

    def test_skill_required_sections_and_no_placeholders(self) -> None:
        headings = ["Objetivo", "Quando utilizar", "Quando não utilizar", "Pré-condições", "Procedimento", "Ferramentas necessárias", "Formato de saída", "Critérios de validação", "Casos de erro", "Exemplo curto"]
        forbidden = re.compile(r"\b(?:TODO|TBD|FIXME|lorem ipsum)\b", re.IGNORECASE)
        for item in self.skills["primary"] + self.skills["shared"]:
            content = (ROOT / item["ref"]).read_text(encoding="utf-8")
            for heading in headings:
                self.assertIn(f"## {heading}", content, item["ref"])
            self.assertIsNone(forbidden.search(content), item["ref"])
            self.assertLess(len(content.splitlines()), 500)

    def test_nineteen_namespaced_command_skills(self) -> None:
        commands = self.skills["commands"]
        self.assertEqual(19, len(commands))
        self.assertIn("clareza", {item["id"] for item in commands})
        expected = {"organizar", "planejar", "construir", "validar", "diagnostico", "revisar-arquitetura", "pesquisar", "memoria", "agentes", "departamentos", "skills", "orcamento", "esteira", "retomar", "relatorio", "auditar", "doctor-org", "ajuda-org"}
        self.assertTrue(expected.issubset({item["id"] for item in commands}))
        for item in commands:
            content = (ROOT / item["ref"]).read_text(encoding="utf-8")
            self.assertIn(f"# /orchestra:{item['id']}", content)
            self.assertIn("## Equivalente CLI", content)
            self.assertLessEqual(item["cli"].count("--json"), 1, item["id"])
            self.assertNotIn("--json --json", content, item["id"])

    def test_command_cli_examples_are_accepted_by_real_parser(self) -> None:
        for item in self.skills["commands"]:
            parser = build_parser()
            argv = item["cli_example_argv"]
            try:
                parsed = parser.parse_args(_normalize_global_options(argv))
            except SystemExit as exc:
                self.assertEqual("ajuda-org", item["id"])
                self.assertEqual(0, exc.code)
                continue
            self.assertTrue(hasattr(parsed, "handler"), item["id"])
            self.assertLessEqual(argv.count("--json"), 1, item["id"])

    def test_clareza_contract(self) -> None:
        content = (ROOT / "skills/clareza/SKILL.md").read_text(encoding="utf-8")
        for value in ["quick", "normal", "high", "APPROVED", "APPROVED_WITH_NOTES", "CHANGES_REQUESTED", "INCONCLUSIVE"]:
            self.assertIn(value, content)
        self.assertIn("no máximo dois especialistas", content)

    def test_hooks_are_real_and_safe(self) -> None:
        hooks = load_json("hooks/hooks.json")["hooks"]
        self.assertTrue({"SessionStart", "PreToolUse", "PostToolUse"}.issubset(hooks))
        guard = (ROOT / "scripts/guard_hook.py").read_text(encoding="utf-8")
        telemetry = (ROOT / "scripts/telemetry_hook.py").read_text(encoding="utf-8")
        self.assertIn("permissionDecision", guard)
        self.assertIn("ORCHESTRA_HOOK_TELEMETRY", telemetry)
        self.assertNotIn("tool_input", telemetry)


if __name__ == "__main__":
    unittest.main()
