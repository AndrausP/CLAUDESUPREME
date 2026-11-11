"""Deterministic workflow state machine."""

from __future__ import annotations

from dataclasses import dataclass

from .errors import ErrorCode, OrchestraError
from .models import TaskStatus


TERMINAL_STATES = frozenset({TaskStatus.COMPLETED, TaskStatus.FAILED, TaskStatus.CANCELLED})

VALID_TRANSITIONS: dict[TaskStatus, frozenset[TaskStatus]] = {
    TaskStatus.CREATED: frozenset({TaskStatus.CLASSIFIED, TaskStatus.CANCELLED, TaskStatus.FAILED}),
    TaskStatus.CLASSIFIED: frozenset({TaskStatus.PLANNED, TaskStatus.READY, TaskStatus.BLOCKED, TaskStatus.CANCELLED, TaskStatus.FAILED}),
    TaskStatus.PLANNED: frozenset({TaskStatus.READY, TaskStatus.BLOCKED, TaskStatus.CANCELLED, TaskStatus.FAILED}),
    TaskStatus.READY: frozenset({TaskStatus.RUNNING, TaskStatus.BLOCKED, TaskStatus.CANCELLED, TaskStatus.FAILED}),
    TaskStatus.RUNNING: frozenset({TaskStatus.REVIEWING, TaskStatus.VALIDATING, TaskStatus.BLOCKED, TaskStatus.REWORK_REQUIRED, TaskStatus.CANCELLED, TaskStatus.FAILED}),
    TaskStatus.BLOCKED: frozenset({TaskStatus.READY, TaskStatus.RUNNING, TaskStatus.CANCELLED, TaskStatus.FAILED}),
    TaskStatus.REVIEWING: frozenset({TaskStatus.VALIDATING, TaskStatus.REWORK_REQUIRED, TaskStatus.BLOCKED, TaskStatus.CANCELLED, TaskStatus.FAILED}),
    TaskStatus.VALIDATING: frozenset({TaskStatus.APPROVED, TaskStatus.REWORK_REQUIRED, TaskStatus.BLOCKED, TaskStatus.CANCELLED, TaskStatus.FAILED}),
    TaskStatus.APPROVED: frozenset({TaskStatus.COMPLETED, TaskStatus.REWORK_REQUIRED, TaskStatus.FAILED}),
    TaskStatus.REWORK_REQUIRED: frozenset({TaskStatus.READY, TaskStatus.RUNNING, TaskStatus.CANCELLED, TaskStatus.FAILED}),
    TaskStatus.COMPLETED: frozenset(),
    TaskStatus.FAILED: frozenset(),
    TaskStatus.CANCELLED: frozenset(),
}


@dataclass(frozen=True, slots=True)
class TransitionRequest:
    task_id: str
    expected_revision: int
    from_status: TaskStatus
    to_status: TaskStatus
    actor_type: str
    actor_id: str
    reason_code: str
    reason: str
    evidence_refs: tuple[str, ...] = ()


class StateMachine:
    @staticmethod
    def validate(request: TransitionRequest, acceptance_criteria: list[dict[str, object]]) -> None:
        if request.to_status not in VALID_TRANSITIONS[request.from_status]:
            raise OrchestraError(
                ErrorCode.INVALID_TRANSITION,
                f"{request.from_status.value} cannot transition to {request.to_status.value}",
                details={"from": request.from_status.value, "to": request.to_status.value},
            )
        if request.to_status is TaskStatus.COMPLETED:
            incomplete = [item.get("id") for item in acceptance_criteria if item.get("status") != "passed"]
            if incomplete or not request.evidence_refs:
                raise OrchestraError(
                    ErrorCode.VALIDATION_INCONCLUSIVE,
                    "COMPLETED requires passed acceptance criteria and evidence",
                    details={"incomplete_criteria": incomplete, "evidence_count": len(request.evidence_refs)},
                )

