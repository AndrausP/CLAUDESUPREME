from __future__ import annotations

from contextlib import redirect_stderr, redirect_stdout
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from orchestra_core import cli
from orchestra_core.models import TaskRecord, TaskStatus, new_id
from orchestra_core.routing import AgentCapability, Router, TaskSignals
from orchestra_core.storage import SQLiteStore


class RealScenarioTests(unittest.TestCase):
    """Eight requested scenarios with expected result and executable proof."""

    def setUp(self) -> None:
        self.router = Router()
        self.candidates = [
            AgentCapability("feature-engineer", frozenset({"backend", "endpoint", "feature"})),
            AgentCapability("ui-implementer", frozenset({"frontend", "component"})),
            AgentCapability("data-modeler", frozenset({"database", "migration"})),
            AgentCapability("defect-investigator", frozenset({"debugging", "intermittent"})),
            AgentCapability("code-review-specialist", frozenset({"review"})),
            AgentCapability("quality-lead", frozenset(), leader=True),
        ]

    def _assert_route(self, signals: TaskSignals, capabilities: set[str], expected_mode: str) -> None:
        # Arrange / Act
        decision = self.router.route(signals, capabilities, self.candidates)

        # Assert
        self.assertEqual(expected_mode, decision.mode.value)
        self.assertTrue(decision.selected_agents)
        self.assertTrue(all(item.reason_code for item in decision.selected_agents))

    def test_Should_UseLeanMode_When_FixingSimpleBug(self) -> None:
        self._assert_route(TaskSignals(mutation=True), {"backend"}, "LEAN")

    def test_Should_UseStandardMode_When_ImplementingEndpoint(self) -> None:
        self._assert_route(
            TaskSignals(mutation=True, areas=2, external_dependencies=1, validations=2),
            {"endpoint", "backend"},
            "STANDARD",
        )

    def test_Should_UseLeanMode_When_CreatingFrontendComponent(self) -> None:
        self._assert_route(TaskSignals(mutation=True, validations=2), {"frontend", "component"}, "LEAN")

    def test_Should_UseDeepMode_When_MigratingDatabase(self) -> None:
        self._assert_route(TaskSignals(data_migration=True, mutation=True), {"database", "migration"}, "DEEP")

    def test_Should_UseStandardMode_When_InvestigatingIntermittentFailure(self) -> None:
        self._assert_route(TaskSignals(uncertainty=3, areas=2, validations=2), {"debugging", "intermittent"}, "STANDARD")

    def test_Should_UseStandardMode_When_ImplementingCompleteFeature(self) -> None:
        self._assert_route(
            TaskSignals(mutation=True, areas=3, external_dependencies=1, validations=2),
            {"feature", "frontend"},
            "STANDARD",
        )

    def test_Should_RequestChanges_When_ReviewFindsKnownFailure(self) -> None:
        # Arrange
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "pyproject.toml").write_text("[project]\nname='qa-fixture'\n", encoding="utf-8")
            (root / ".git").mkdir()
            (root / "tests").mkdir()
            stdout, stderr = io.StringIO(), io.StringIO()
            failed_check = {"command": "qa-known-failure", "exit_code": 1, "stdout": "", "stderr": "known failure"}

            # Act
            with patch("orchestra_core.cli._run_readonly", return_value=failed_check), redirect_stdout(stdout), redirect_stderr(stderr):
                exit_code = cli.main(["clareza", "HIGH", ".", "--security", "--architecture", "--project", directory, "--json"])
            report = json.loads(stdout.getvalue())

            # Assert
            self.assertEqual(2, exit_code)
            self.assertEqual("CHANGES_REQUESTED", report["verdict"])
            self.assertLessEqual(len(report["specialists"]), 2)
            self.assertTrue(report["findings"])

    def test_Should_RecoverAfterInterruption_When_CheckpointExists(self) -> None:
        # Arrange
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            path = root / "state.db"
            store = SQLiteStore(path)
            project_id = new_id()
            store.ensure_project(project_id, "recovery")
            task = store.create_task(TaskRecord("Interrupted", "Resume safely", project_id, "feature-engineer"))
            store.save_checkpoint(task.task_id, TaskStatus.CREATED, "before-interruption", {"safe": True})
            store.close()

            # Act
            reopened = SQLiteStore(path)
            recovered = reopened.recoverable_tasks(project_id)
            checkpoint = reopened.latest_checkpoint(task.task_id)
            reopened.close()

            # Assert
            self.assertEqual([task.task_id], [item.task_id for item in recovered])
            self.assertEqual("before-interruption", checkpoint["step"])


if __name__ == "__main__":
    unittest.main()

