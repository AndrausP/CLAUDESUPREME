"""Typed errors used at every trust boundary."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Generic, TypeVar


class ErrorCode(StrEnum):
    INVALID_SCHEMA = "INVALID_SCHEMA"
    INVALID_TRANSITION = "INVALID_TRANSITION"
    REVISION_CONFLICT = "REVISION_CONFLICT"
    BUDGET_EXHAUSTED = "BUDGET_EXHAUSTED"
    RETRY_LIMIT = "RETRY_LIMIT"
    REWORK_LOOP = "REWORK_LOOP"
    DEPENDENCY_BLOCKED = "DEPENDENCY_BLOCKED"
    PERMISSION_DENIED = "PERMISSION_DENIED"
    UNSAFE_EXTENSION = "UNSAFE_EXTENSION"
    CHECKSUM_MISMATCH = "CHECKSUM_MISMATCH"
    INCOMPATIBLE_VERSION = "INCOMPATIBLE_VERSION"
    STORAGE_FAILURE = "STORAGE_FAILURE"
    VALIDATION_INCONCLUSIVE = "VALIDATION_INCONCLUSIVE"
    NOT_FOUND = "NOT_FOUND"


@dataclass
class OrchestraError(Exception):
    code: ErrorCode
    message: str
    retryable: bool = False
    details: dict[str, object] = field(default_factory=dict)
    correlation_id: str | None = None

    def __str__(self) -> str:
        return f"{self.code}: {self.message}"

    def to_dict(self) -> dict[str, object]:
        return {
            "error": {
                "code": self.code.value,
                "message": self.message,
                "retryable": self.retryable,
                "details": self.details,
                "correlation_id": self.correlation_id,
            }
        }


T = TypeVar("T")


@dataclass(frozen=True, slots=True)
class Result(Generic[T]):
    value: T | None = None
    error: OrchestraError | None = None

    @property
    def ok(self) -> bool:
        return self.error is None

    def unwrap(self) -> T:
        if self.error is not None:
            raise self.error
        return self.value  # type: ignore[return-value]

    @classmethod
    def success(cls, value: T) -> "Result[T]":
        return cls(value=value)

    @classmethod
    def failure(cls, error: OrchestraError) -> "Result[T]":
        return cls(error=error)

