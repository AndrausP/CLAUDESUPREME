"""Domain models. This module has no I/O dependencies."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import StrEnum
from typing import Any
from uuid import uuid4


def utc_now() -> str:
    return datetime.now(UTC).isoformat().replace("+00:00", "Z")


def new_id() -> str:
    return str(uuid4())


class TaskStatus(StrEnum):
    CREATED = "CREATED"
    CLASSIFIED = "CLASSIFIED"
    PLANNED = "PLANNED"
    READY = "READY"
    RUNNING = "RUNNING"
    BLOCKED = "BLOCKED"
    REVIEWING = "REVIEWING"
    VALIDATING = "VALIDATING"
    APPROVED = "APPROVED"
    REWORK_REQUIRED = "REWORK_REQUIRED"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"


class RoutingMode(StrEnum):
    DIRECT = "DIRECT"
    LEAN = "LEAN"
    STANDARD = "STANDARD"
    DEEP = "DEEP"


class RiskLevel(StrEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class BudgetProfile(StrEnum):
    ECONOMY = "ECONOMY"
    BALANCED = "BALANCED"
    QUALITY = "QUALITY"
    CRITICAL = "CRITICAL"


class MetricProvenance(StrEnum):
    OBSERVED = "observed"
    CALCULATED = "calculated"
    ESTIMATED = "estimated"
    UNKNOWN = "unknown"


class MemoryType(StrEnum):
    ORGANIZATIONAL = "organizational"
    PROJECT = "project"
    DEPARTMENT_AGENT = "department-agent"
    EPISODIC = "episodic"


class MemoryStatus(StrEnum):
    PROPOSED = "PROPOSED"
    VERIFIED = "VERIFIED"
    OUTDATED = "OUTDATED"
    SUPERSEDED = "SUPERSEDED"
    REJECTED = "REJECTED"


@dataclass(slots=True)
class CandidateDecision:
    id: str
    reason_code: str

    def to_dict(self) -> dict[str, str]:
        return {"id": self.id, "reason_code": self.reason_code}


@dataclass(slots=True)
class TaskRecord:
    title: str
    objective: str
    project_id: str
    owner: str
    task_id: str = field(default_factory=new_id)
    parent_task_id: str | None = None
    attempt_of: str | None = None
    correlation_id: str = field(default_factory=new_id)
    mode: RoutingMode = RoutingMode.DIRECT
    risk: RiskLevel = RiskLevel.LOW
    status: TaskStatus = TaskStatus.CREATED
    selected_agents: list[CandidateDecision] = field(default_factory=list)
    rejected_candidates: list[CandidateDecision] = field(default_factory=list)
    acceptance_criteria: list[dict[str, Any]] = field(default_factory=list)
    dependencies: list[str] = field(default_factory=list)
    budget_profile: BudgetProfile = BudgetProfile.BALANCED
    revision: int = 0
    created_at: str = field(default_factory=utc_now)
    updated_at: str = field(default_factory=utc_now)

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": "1.0.0",
            "task_id": self.task_id,
            "parent_task_id": self.parent_task_id,
            "attempt_of": self.attempt_of,
            "project_id": self.project_id,
            "correlation_id": self.correlation_id,
            "title": self.title,
            "objective": self.objective,
            "mode": self.mode.value,
            "risk": self.risk.value,
            "status": self.status.value,
            "owner": self.owner,
            "selected_agents": [item.to_dict() for item in self.selected_agents],
            "rejected_candidates": [item.to_dict() for item in self.rejected_candidates],
            "acceptance_criteria": self.acceptance_criteria,
            "dependencies": self.dependencies,
            "budget_profile": self.budget_profile.value,
            "revision": self.revision,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }


@dataclass(frozen=True, slots=True)
class Metric:
    name: str
    value: int | float | None
    unit: str
    provenance: MetricProvenance
    source: str
    measured_at: str = field(default_factory=utc_now)

    def __post_init__(self) -> None:
        if self.provenance is MetricProvenance.UNKNOWN and self.value is not None:
            raise ValueError("unknown metrics must use value=None")

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "value": self.value,
            "unit": self.unit,
            "provenance": self.provenance.value,
            "source": self.source,
            "measured_at": self.measured_at,
        }

