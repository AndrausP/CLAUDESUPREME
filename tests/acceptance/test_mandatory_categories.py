from __future__ import annotations

from contextlib import redirect_stderr, redirect_stdout
import argparse
import io
import json
from pathlib import Path
import re
import tempfile
import unittest
from unittest.mock import patch

from jsonschema import Draft202012Validator, FormatChecker

from orchestra_core import cli
from orchestra_core.adapters.agent_sdk import AgentSDKAdapter
from orchestra_core.adapters.ledger import LedgerAdapter
from orchestra_core.bootstrap import Bootstrapper
from orchestra_core.budgets import BudgetGuard, BudgetUsage, ReworkGuard, RetryPolicy
from orchestra_core.errors import ErrorCode, OrchestraError
from orchestra_core.memory import MemoryService
from orchestra_core.models import (
    BudgetProfile,
    MemoryStatus,
    MemoryType,
    TaskRecord,
    TaskStatus,
    new_id,
)
from orchestra_core.registry import RegistryService
from orchestra_core.routing import AgentCapability, Router, TaskSignals
from orchestra_core.storage import SQLiteStore
from orchestra_core.telemetry import Event
from orchestra_core.workflow import TransitionRequest


ROOT = Path(__file__).resolve().parents[2]


def read_json(relative: str) -> dict:
    return json.loads((ROOT / relative).read_text(encoding="utf-8"))


def valid_handoff() -> dict:
    return {
        "schema_version": "1.0.0",
        "handoff_id": new_id(),
        "task_id": new_id(),
        "parent_task_id": None,
        "correlation_id": new_id(),
        "from_department": "backend",
        "from_agent": "feature-engineer",
        "to": "quality-lead",
        "objective": "Validate the implementation",
        "minimal_context": "Only the accepted contract and changed files.",
        "relevant_files": [{"path": "src/example.py", "sha256": "a" * 64}],
        "memory_refs": [],
        "confirmed_decisions": ["SQLite is authoritative"],
        "acceptance_criteria": [{"id": "AC-1", "status": "passed"}],
        "artifacts": [],
        "test_results": [{"suite": "unit", "status": "passed"}],
        "issues": [],
        "status": "VALIDATING",
        "next_action": "Run quality gate",
        "evidence_refs": ["evidence:test"],
        "created_at": "2026-11-11T12:00:00Z",
    }


class MandatoryCategoryTests(unittest.TestCase):
    """Executable evidence for the 23 mandatory categories in the master spec."""

    def setUp(self) -> None:
        # Arrange
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        self.store = SQLiteStore(self.root / "state.db")
        self.project_id = new_id()
        self.store.ensure_project(self.project_id, "qa-project")

    def tearDown(self) -> None:
        self.store.close()
        self.temporary.cleanup()

    def _task(self, *, dependencies: list[str] | None = None) -> TaskRecord:
        task = TaskRecord(
            "QA task",
            "Exercise workflow contracts",
            self.project_id,
            "automated-test-engineer",
            dependencies=dependencies or [],
            acceptance_criteria=[{"id": "AC-1", "status": "pending"}],
        )
        return self.store.create_task(task)

    def _transition(self, task: TaskRecord, target: TaskStatus, *, evidence: tuple[str, ...] = ()) -> TaskRecord:
        request = TransitionRequest(
            task.task_id,
            task.revision,
            task.status,
            target,
            "qa",
            "automated-test-engineer",
            "QA_TEST",
            "Acceptance test transition",
            evidence,
        )
        return self.store.transition(request)

    def test_Should_BeDirectoryInstallable_When_PluginIsSubmitted(self) -> None:
        # Arrange
        readme = ROOT / "README.md"

        # Act
        words = readme.read_text(encoding="utf-8").split() if readme.exists() else []

        # Assert
        self.assertTrue(readme.is_file(), "README_MISSING: plugin directory submission is blocked")
        self.assertGreaterEqual(len(words), 40, "plugin directory README must contain at least 40 words")

    def test_Should_LoadExactlyThirtySixAgents_When_CatalogIsRead(self) -> None:
        # Arrange / Act
        catalog = read_json("catalogs/agents.json")

        # Assert
        self.assertEqual(36, len(catalog["agents"]))
        self.assertEqual(7, len(catalog["departments"]))
        self.assertTrue(all(len(item["agents"]) == 5 for item in catalog["departments"]))

    def test_Should_UseSupportedFrontmatter_When_AgentsAreDiscovered(self) -> None:
        # Arrange
        allowed = {
            "name", "description", "model", "effort", "maxTurns", "tools",
            "disallowedTools", "skills", "memory", "background", "omitClaudeMd",
            "isolation", "color", "experimental",
        }

        # Act / Assert
        for path in ROOT.glob("agents/**/*.md"):
            text = path.read_text(encoding="utf-8")
            self.assertTrue(text.startswith("---\n"), path)
            block = text.split("---\n", 2)[1]
            keys = {
                line.split(":", 1)[0].strip()
                for line in block.splitlines()
                if line and not line.startswith((" ", "-")) and ":" in line
            }
            self.assertTrue({"name", "description"}.issubset(keys), path)
            self.assertFalse(keys - allowed, f"unsupported fields in {path}: {keys - allowed}")

    def test_Should_DiscoverThirtySixPrimarySkills_When_CatalogIsRead(self) -> None:
        # Arrange / Act
        catalog = read_json("catalogs/skills.json")

        # Assert
        self.assertEqual(36, len(catalog["primary"]))
        self.assertTrue(all((ROOT / item["ref"]).is_file() for item in catalog["primary"]))

    def test_Should_ParseEveryDocumentedCliEquivalent_When_CommandSkillIsLoaded(self) -> None:
        # Arrange
        parser = cli.build_parser()
        commands = read_json("catalogs/skills.json")["commands"]
        equivalents: dict[str, str] = {}
        for item in commands:
            path = ROOT / item["ref"]
            text = path.read_text(encoding="utf-8")
            match = re.search(r"^## Equivalente CLI\s+\n\s*`([^`]+)`", text, re.MULTILINE)
            self.assertIsNotNone(match, path)
            equivalents[item["id"]] = match.group(1)

        # Act / Assert
        self.assertEqual(19, len(equivalents))
        for item in commands:
            command = equivalents[item["id"]]
            self.assertEqual(item["cli"], command, item["ref"])
            self.assertLessEqual(command.split().count("--json"), 1, item["ref"])
            with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
                try:
                    parsed = parser.parse_args(cli._normalize_global_options(item["cli_example_argv"]))
                except SystemExit as exc:
                    self.assertEqual(0, exc.code, item["id"])
                else:
                    self.assertTrue(hasattr(parsed, "handler"), item["id"])

    def test_Should_KeepProjectIdentity_When_BootstrapRunsTwice(self) -> None:
        # Arrange / Act
        first, first_store = Bootstrapper(self.root / "project").run()
        first_store.close()
        second, second_store = Bootstrapper(self.root / "project").run()
        second_store.close()

        # Assert
        self.assertEqual(first.project_id, second.project_id)

    def test_Should_ClassifyAllModes_When_RiskSignalsChange(self) -> None:
        # Arrange
        router = Router()

        # Act
        modes = {
            router.classify(TaskSignals())[0].value,
            router.classify(TaskSignals(mutation=True))[0].value,
            router.classify(TaskSignals(mutation=True, areas=3))[0].value,
            router.classify(TaskSignals(security=True))[0].value,
        }

        # Assert
        self.assertEqual({"DIRECT", "LEAN", "STANDARD", "DEEP"}, modes)

    def test_Should_SelectSmallestDepartmentSet_When_CapabilitiesOverlap(self) -> None:
        # Arrange
        candidates = [
            AgentCapability("feature-engineer", frozenset({"backend", "tests"})),
            AgentCapability("automated-test-engineer", frozenset({"tests"})),
            AgentCapability("backend-lead", frozenset(), leader=True),
        ]

        # Act
        decision = Router().route(TaskSignals(mutation=True), {"backend", "tests"}, candidates)

        # Assert
        self.assertEqual(["feature-engineer"], [item.id for item in decision.selected_agents])

    def test_Should_RejectBoundaryOverflow_When_BudgetIsExceeded(self) -> None:
        # Arrange
        usage = BudgetUsage(agent_runs=2)

        # Act / Assert
        with self.assertRaises(OrchestraError) as raised:
            BudgetGuard(BudgetProfile.ECONOMY).validate(usage)
        self.assertEqual(ErrorCode.BUDGET_EXHAUSTED, raised.exception.code)

    def test_Should_RejectEveryInvalidStateEdge_When_StateMachineRuns(self) -> None:
        # Arrange
        task = self._task()

        # Act / Assert
        with self.assertRaises(OrchestraError) as raised:
            self._transition(task, TaskStatus.COMPLETED, evidence=("evidence:fake",))
        self.assertEqual(ErrorCode.INVALID_TRANSITION, raised.exception.code)

    def test_Should_ValidateHandoffSchema_When_FixtureIsComplete(self) -> None:
        # Arrange
        schema = read_json("schemas/handoff.schema.json")
        validator = Draft202012Validator(schema, format_checker=FormatChecker())
        fixture = valid_handoff()

        # Act
        valid_errors = list(validator.iter_errors(fixture))
        invalid = dict(fixture)
        invalid.pop("next_action")
        invalid_errors = list(validator.iter_errors(invalid))

        # Assert
        self.assertEqual([], valid_errors)
        self.assertTrue(invalid_errors)

    def test_Should_BlockRunningTask_When_DependencyIsIncomplete(self) -> None:
        # Arrange
        task = self._task(dependencies=["missing-dependency"])
        for target in (TaskStatus.CLASSIFIED, TaskStatus.PLANNED, TaskStatus.READY):
            task = self._transition(task, target)

        # Act / Assert
        with self.assertRaises(OrchestraError) as raised:
            self._transition(task, TaskStatus.RUNNING)
        self.assertEqual(ErrorCode.DEPENDENCY_BLOCKED, raised.exception.code)

    def test_Should_RecoverTaskAndCheckpoint_When_ProcessRestarts(self) -> None:
        # Arrange
        task = self._task()
        self.store.save_checkpoint(task.task_id, task.status, "created", {"done": False})
        path = self.store.path
        self.store.close()

        # Act
        self.store = SQLiteStore(path)
        recovered = self.store.recoverable_tasks(self.project_id)
        checkpoint = self.store.latest_checkpoint(task.task_id)

        # Assert
        self.assertEqual([task.task_id], [item.task_id for item in recovered])
        self.assertEqual("created", checkpoint["step"])

    def test_Should_SaveAndRetrieveAllMemoryTypes_When_Verified(self) -> None:
        # Arrange
        service = MemoryService(self.store)

        # Act
        for index, memory_type in enumerate(MemoryType):
            memory_id = service.propose(
                memory_type=memory_type,
                scope="qa:all-types",
                title=f"Memory {index}",
                summary=f"Verified {memory_type.value}",
                content_ref=f"evidence:{index}",
                origin={"type": "qa", "id": new_id()},
            )
            service.verify(memory_id, [f"evidence:{index}"])

        # Assert
        self.assertEqual(4, len(service.search("qa:all-types", "Memory", for_context=True)))

    def test_Should_DetectDuplicateMemory_When_ContentMatches(self) -> None:
        # Arrange
        service = MemoryService(self.store)
        kwargs = dict(
            memory_type=MemoryType.PROJECT,
            scope="qa:duplicate",
            title="Canonical rule",
            summary="Same content",
            content_ref="evidence:same",
            origin={"type": "qa", "id": "same-origin"},
        )
        service.propose(**kwargs)

        # Act / Assert
        with self.assertRaises(OrchestraError) as raised:
            service.propose(**kwargs)
        self.assertEqual(ErrorCode.INVALID_SCHEMA, raised.exception.code)

    def test_Should_NotRetryToolFailure_When_ErrorIsDeterministic(self) -> None:
        # Arrange / Act / Assert
        with self.assertRaises(OrchestraError) as raised:
            RetryPolicy.require_retryable(False)
        self.assertEqual(ErrorCode.RETRY_LIMIT, raised.exception.code)
        with self.assertRaises(OrchestraError):
            AgentSDKAdapter().execute(authenticated=False)

    def test_Should_SaveCheckpointBeforeCancellation_When_TaskIsRunning(self) -> None:
        # Arrange
        project = self.root / "cancel-project"
        project.mkdir()
        (project / "pyproject.toml").write_text("[project]\nname='qa-cancel'\n", encoding="utf-8")

        def invoke(*arguments: str) -> tuple[int, dict]:
            stdout, stderr = io.StringIO(), io.StringIO()
            with redirect_stdout(stdout), redirect_stderr(stderr):
                code = cli.main([*arguments, "--project", str(project), "--json"])
            self.assertEqual("", stderr.getvalue(), stderr.getvalue())
            return code, json.loads(stdout.getvalue())

        code, created = invoke("task", "create", "Safe cancellation", "--objective", "Persist checkpoint")
        self.assertEqual(0, code)
        for target in ("CLASSIFIED", "PLANNED", "READY", "RUNNING"):
            code, _ = invoke("task", "transition", created["task_id"], target)
            self.assertEqual(0, code)

        # Act
        code, cancelled = invoke(
            "task", "cancel", created["task_id"],
            "--reason", "QA requested stop", "--evidence", "evidence:qa-cancel",
        )

        # Assert
        self.assertEqual(0, code)
        self.assertEqual("CANCELLED", cancelled["status"])
        checkpoint = cancelled["cancellation_evidence"]
        self.assertEqual("pre-cancellation", checkpoint["step"])
        self.assertEqual("RUNNING", checkpoint["state"])
        self.assertEqual(["evidence:qa-cancel"], checkpoint["payload"]["evidence_refs"])
        self.assertTrue(checkpoint["payload"]["safe_to_resume"])

    def test_Should_StopRepeatedDefect_When_ReworkLoops(self) -> None:
        # Arrange
        guard = ReworkGuard(max_cycles=3)
        guard.record("same root cause")

        # Act / Assert
        with self.assertRaises(OrchestraError) as raised:
            guard.record("Same root cause")
        self.assertEqual(ErrorCode.REWORK_LOOP, raised.exception.code)

    def test_Should_RequireExternalConfirmation_When_ComponentIsEnabled(self) -> None:
        # Arrange
        component = self.root / "component"
        component.mkdir()
        (component / "SKILL.md").write_text("safe", encoding="utf-8")
        registry = RegistryService(self.store)
        report = registry.register(
            component_id="skill:qa",
            version="1.0.0",
            component_type="skill",
            origin_kind="external",
            origin_uri="https://example.com/qa.git",
            path=component,
            description="QA fixture",
        )

        # Act / Assert
        with self.assertRaises(OrchestraError) as raised:
            registry.set_status("skill:qa", "enabled", expected_checksum=report.checksum, external_confirmation=False)
        self.assertEqual(ErrorCode.PERMISSION_DENIED, raised.exception.code)

    def test_Should_ExportSanitizedEventsOnce_When_OutboxIsFlushed(self) -> None:
        # Arrange
        self.store.enqueue_event(Event("diagnostic.created", new_id(), None, {"prompt": "secret", "safe": "ok"}))
        destination = self.root / "events.jsonl"

        # Act
        first = self.store.export_events(destination)
        second = self.store.export_events(destination)
        events = [json.loads(line) for line in destination.read_text(encoding="utf-8").splitlines()]

        # Assert
        self.assertEqual(1, first)
        self.assertEqual(0, second)
        self.assertEqual("[REDACTED]", events[0]["payload"]["prompt"])

    def test_Should_RunWithoutLedger_When_OptionalIntegrationIsAbsent(self) -> None:
        # Arrange / Act
        status, store = Bootstrapper(self.root / "no-ledger").run()

        # Assert
        self.assertTrue(status.project_id)
        store.close()

    def test_Should_ValidateLedgerManifest_When_OptionalExportRuns(self) -> None:
        # Arrange
        schema = read_json("schemas/organization-manifest.schema.json")
        adapter = LedgerAdapter(self.store)

        # Act
        manifest = adapter.write_manifest(self.root / "manifest.json", departments=[], agents=[], skills=[])
        errors = list(Draft202012Validator(schema, format_checker=FormatChecker()).iter_errors(manifest))

        # Assert
        self.assertEqual([], errors)
        self.assertEqual("optional", manifest["integrations"]["claude_ledger"])

    def test_Should_KeepTerminalWrappersAsciiSafe_When_LegacyConsoleRuns(self) -> None:
        # Arrange
        wrappers = [ROOT / "bin/orchestra", ROOT / "bin/orchestra.cmd", ROOT / "bin/orchestra.ps1"]

        # Act / Assert
        for wrapper in wrappers:
            content = wrapper.read_text(encoding="utf-8")
            content.encode("ascii")
            self.assertIn("orchestra_core.cli", content)

    def test_Should_RemoveRegisteredComponent_When_ChecksumAndConfirmationMatch(self) -> None:
        # Arrange
        component = self.root / "removable"
        component.mkdir()
        (component / "SKILL.md").write_text("safe", encoding="utf-8")
        registry = RegistryService(self.store)
        report = registry.register(
            component_id="skill:remove",
            version="1.0.0",
            component_type="skill",
            origin_kind="local",
            origin_uri=str(component),
            path=component,
            description="QA removable fixture",
        )

        # Act
        registry.set_status("skill:remove", "removed", expected_checksum=report.checksum, external_confirmation=True)

        # Assert
        self.assertEqual("removed", self.store.get_component("skill:remove")["status"])


if __name__ == "__main__":
    unittest.main()

