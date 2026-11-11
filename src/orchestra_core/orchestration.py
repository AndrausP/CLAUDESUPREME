"""Application service coordinating domain policies through ports."""

from __future__ import annotations

from dataclasses import dataclass

from .models import TaskRecord
from .routing import AgentCapability, Router, TaskSignals
from .storage import SQLiteStore
from .workflow import TransitionRequest


@dataclass(slots=True)
class OrchestraService:
    store: SQLiteStore
    router: Router

    @classmethod
    def with_defaults(cls, store: SQLiteStore) -> "OrchestraService":
        return cls(store, Router())

    def create_task(self, task: TaskRecord) -> TaskRecord:
        return self.store.create_task(task)

    def classify(
        self,
        task_id: str,
        expected_revision: int,
        signals: TaskSignals,
        required_capabilities: set[str],
        candidates: list[AgentCapability],
    ) -> TaskRecord:
        decision = self.router.route(signals, required_capabilities, candidates)
        return self.store.update_task_classification(
            task_id,
            expected_revision,
            decision.mode,
            decision.risk,
            decision.selected_agents,
            decision.rejected_candidates,
        )

    def transition(self, request: TransitionRequest) -> TaskRecord:
        return self.store.transition(request)

