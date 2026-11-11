from __future__ import annotations

import json
from pathlib import Path
import tempfile
import unittest

from orchestra_core.errors import ErrorCode, OrchestraError
from orchestra_core.models import TaskRecord, TaskStatus, new_id
from orchestra_core.routing import AgentCapability, Router, TaskSignals
from orchestra_core.storage import SQLiteStore
from orchestra_core.workflow import TransitionRequest


class StorageTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.store = SQLiteStore(self.root / "state.db")
        self.project_id = new_id()
        self.store.ensure_project(self.project_id, "test-project")

    def tearDown(self) -> None:
        self.store.close()
        self.temp.cleanup()

    def create(self) -> TaskRecord:
        task = TaskRecord("Test", "Verify state", self.project_id, "feature", acceptance_criteria=[{"id": "AC-1", "status": "pending"}])
        return self.store.create_task(task)

    def request(self, task: TaskRecord, target: TaskStatus, evidence: tuple[str, ...] = ()) -> TransitionRequest:
        return TransitionRequest(task.task_id, task.revision, task.status, target, "agent", "tester", "TEST", "test", evidence)

    def test_transactional_lifecycle_and_outbox(self) -> None:
        task = self.create()
        route = Router().route(TaskSignals(mutation=True), {"backend"}, [AgentCapability("feature", frozenset({"backend"}))])
        task = self.store.update_task_classification(task.task_id, task.revision, route.mode, route.risk, route.selected_agents, route.rejected_candidates)
        for target in (TaskStatus.PLANNED, TaskStatus.READY, TaskStatus.RUNNING, TaskStatus.VALIDATING, TaskStatus.APPROVED):
            task = self.store.transition(self.request(task, target))
        task = self.store.mark_criteria(task.task_id, [{"id": "AC-1", "status": "passed"}], task.revision)
        task = self.store.transition(self.request(task, TaskStatus.COMPLETED, ("evidence:test",)))
        self.assertEqual(TaskStatus.COMPLETED, task.status)
        destination = self.root / "events.jsonl"
        exported = self.store.export_events(destination)
        self.assertGreater(exported, 1)
        self.assertEqual(0, self.store.export_events(destination))
        ids = [json.loads(line)["event_id"] for line in destination.read_text(encoding="utf-8").splitlines()]
        self.assertEqual(len(ids), len(set(ids)))

    def test_revision_conflict_is_typed(self) -> None:
        task = self.create()
        request = TransitionRequest(task.task_id, 99, TaskStatus.CREATED, TaskStatus.CLASSIFIED, "system", "router", "TEST", "test")
        with self.assertRaises(OrchestraError) as raised:
            self.store.transition(request)
        self.assertEqual(ErrorCode.REVISION_CONFLICT, raised.exception.code)

    def test_running_is_blocked_until_all_dependencies_are_completed(self) -> None:
        incomplete = self.store.create_task(TaskRecord("Dependency", "Finish first", self.project_id, "feature"))
        missing_id = new_id()
        dependent = self.store.create_task(TaskRecord(
            "Dependent",
            "Wait for dependencies",
            self.project_id,
            "feature",
            status=TaskStatus.READY,
            dependencies=[incomplete.task_id, missing_id],
        ))

        with self.assertRaises(OrchestraError) as raised:
            self.store.transition(self.request(dependent, TaskStatus.RUNNING))

        self.assertEqual(ErrorCode.DEPENDENCY_BLOCKED, raised.exception.code)
        self.assertEqual(
            [
                {"task_id": incomplete.task_id, "status": TaskStatus.CREATED.value},
                {"task_id": missing_id, "status": "NOT_FOUND"},
            ],
            raised.exception.details["blocked_dependencies"],
        )
        unchanged = self.store.get_task(dependent.task_id)
        self.assertEqual(TaskStatus.READY, unchanged.status)
        self.assertEqual(dependent.revision, unchanged.revision)
        transition_count = self.store.connection.execute(
            "SELECT count(*) FROM transitions WHERE task_id=?",
            (dependent.task_id,),
        ).fetchone()[0]
        outbox_count = self.store.connection.execute(
            "SELECT count(*) FROM event_outbox WHERE event_json LIKE ?",
            (f'%"task_id":"{dependent.task_id}"%',),
        ).fetchone()[0]
        self.assertEqual(0, transition_count)
        self.assertEqual(1, outbox_count)  # task.created only; no transition event leaked

    def test_running_is_allowed_when_all_dependencies_are_completed(self) -> None:
        completed = self.store.create_task(TaskRecord(
            "Dependency",
            "Already complete",
            self.project_id,
            "feature",
            status=TaskStatus.COMPLETED,
        ))
        dependent = self.store.create_task(TaskRecord(
            "Dependent",
            "Can start",
            self.project_id,
            "feature",
            status=TaskStatus.READY,
            dependencies=[completed.task_id],
        ))

        running = self.store.transition(self.request(dependent, TaskStatus.RUNNING))

        self.assertEqual(TaskStatus.RUNNING, running.status)
        self.assertEqual(dependent.revision + 1, running.revision)

    def test_checkpoint_and_recovery(self) -> None:
        task = self.create()
        self.store.save_checkpoint(task.task_id, task.status, "classification", {"prompt": "must not persist", "done": []})
        checkpoint = self.store.latest_checkpoint(task.task_id)
        self.assertIsNotNone(checkpoint)
        self.assertEqual("[REDACTED]", checkpoint["payload"]["prompt"])
        self.assertEqual([task.task_id], [item.task_id for item in self.store.recoverable_tasks(self.project_id)])

    def test_failed_task_resumes_as_child_attempt(self) -> None:
        task = self.create()
        task = self.store.transition(self.request(task, TaskStatus.FAILED))
        child = self.store.create_child_attempt(task.task_id)
        self.assertEqual(task.task_id, child.parent_task_id)
        self.assertEqual(TaskStatus.CREATED, child.status)


if __name__ == "__main__":
    unittest.main()

