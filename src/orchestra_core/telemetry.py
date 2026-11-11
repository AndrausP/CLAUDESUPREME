"""Versioned local events and honest metric helpers."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .models import Metric, MetricProvenance, new_id, utc_now
from .sanitize import digest, sanitize


EVENT_TYPES = frozenset({
    "task.created",
    "task.classified",
    "workflow.started",
    "agent.started",
    "agent.completed",
    "tool.completed",
    "handoff.created",
    "validation.completed",
    "memory.proposed",
    "diagnostic.created",
    "budget.warning",
    "task.completed",
    "task.failed",
    "task.transitioned",
    "bootstrap.completed",
    "component.registered",
})


@dataclass(frozen=True, slots=True)
class Event:
    event_type: str
    correlation_id: str
    task_id: str | None
    payload: dict[str, Any]
    sequence: int = 0
    event_id: str = field(default_factory=new_id)
    causation_id: str | None = None
    occurred_at: str = field(default_factory=utc_now)
    source_component: str = "orchestra-core"
    source_version: str = "0.1.0"

    def __post_init__(self) -> None:
        if self.event_type not in EVENT_TYPES:
            raise ValueError(f"unsupported event_type: {self.event_type}")

    def to_dict(self) -> dict[str, Any]:
        payload = sanitize(self.payload)
        return {
            "schema_version": "1.0.0",
            "event_id": self.event_id,
            "event_type": self.event_type,
            "correlation_id": self.correlation_id,
            "causation_id": self.causation_id,
            "task_id": self.task_id,
            "source": {"component": self.source_component, "version": self.source_version},
            "occurred_at": self.occurred_at,
            "sequence": self.sequence,
            "data_classification": "internal",
            "payload": payload,
            "payload_sha256": digest(payload),
        }


def unavailable_metric(name: str, unit: str, reason: str) -> Metric:
    return Metric(name, None, unit, MetricProvenance.UNKNOWN, reason)


class OptionalOtelAdapter:
    """No-op unless an OpenTelemetry implementation is explicitly injected."""

    def __init__(self, exporter: object | None = None):
        self.exporter = exporter

    @property
    def available(self) -> bool:
        return self.exporter is not None and hasattr(self.exporter, "emit")

    def emit(self, event: dict[str, Any]) -> bool:
        if not self.available:
            return False
        # The injected exporter remains optional and receives only sanitized data.
        self.exporter.emit(sanitize(event))  # type: ignore[union-attr]
        return True

