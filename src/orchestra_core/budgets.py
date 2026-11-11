"""Enforceable operation budgets and bounded retry/rework policies."""

from __future__ import annotations

from dataclasses import dataclass, field
from hashlib import sha256
import random

from .errors import ErrorCode, OrchestraError
from .models import BudgetProfile


@dataclass(frozen=True, slots=True)
class BudgetLimits:
    max_agent_runs: int
    max_parallel_agents: int
    max_retries_per_step: int
    max_rework_cycles: int
    max_duration_seconds: int
    max_artifact_bytes: int
    max_tokens: int | None = None


PROFILES: dict[BudgetProfile, BudgetLimits] = {
    BudgetProfile.ECONOMY: BudgetLimits(1, 1, 1, 1, 900, 2_000_000),
    BudgetProfile.BALANCED: BudgetLimits(3, 2, 2, 2, 3_600, 10_485_760),
    BudgetProfile.QUALITY: BudgetLimits(6, 3, 3, 3, 7_200, 25_000_000),
    BudgetProfile.CRITICAL: BudgetLimits(8, 3, 3, 3, 10_800, 25_000_000),
}


@dataclass(slots=True)
class BudgetUsage:
    agent_runs: int = 0
    parallel_agents: int = 0
    retries: int = 0
    rework_cycles: int = 0
    duration_seconds: float = 0
    artifact_bytes: int = 0
    tokens: int | None = None


class BudgetGuard:
    def __init__(self, profile: BudgetProfile):
        self.profile = profile
        self.limits = PROFILES[profile]

    def validate(self, usage: BudgetUsage) -> None:
        checks = {
            "agent_runs": (usage.agent_runs, self.limits.max_agent_runs),
            "parallel_agents": (usage.parallel_agents, self.limits.max_parallel_agents),
            "retries": (usage.retries, self.limits.max_retries_per_step),
            "rework_cycles": (usage.rework_cycles, self.limits.max_rework_cycles),
            "duration_seconds": (usage.duration_seconds, self.limits.max_duration_seconds),
            "artifact_bytes": (usage.artifact_bytes, self.limits.max_artifact_bytes),
        }
        for name, (value, limit) in checks.items():
            if value > limit:
                raise OrchestraError(ErrorCode.BUDGET_EXHAUSTED, f"{name} budget exhausted", details={"value": value, "limit": limit})
        if self.limits.max_tokens is not None and usage.tokens is not None and usage.tokens > self.limits.max_tokens:
            raise OrchestraError(ErrorCode.BUDGET_EXHAUSTED, "token budget exhausted")


class RetryPolicy:
    @staticmethod
    def next_delay(attempt: int, base_seconds: float = 1.0, maximum: float = 60.0, seed: int | None = None) -> float:
        if attempt < 1:
            raise ValueError("attempt must be >= 1")
        rng = random.Random(seed)
        exponential = min(maximum, base_seconds * (2 ** (attempt - 1)))
        return min(maximum, exponential * rng.uniform(0.8, 1.2))

    @staticmethod
    def require_retryable(retryable: bool) -> None:
        if not retryable:
            raise OrchestraError(ErrorCode.RETRY_LIMIT, "deterministic failures are not retried")


@dataclass(slots=True)
class ReworkGuard:
    max_cycles: int
    signatures: dict[str, int] = field(default_factory=dict)
    cycles: int = 0

    def record(self, defect: str) -> str:
        signature = sha256(defect.strip().lower().encode("utf-8")).hexdigest()
        self.cycles += 1
        self.signatures[signature] = self.signatures.get(signature, 0) + 1
        if self.cycles > self.max_cycles or self.signatures[signature] > 1:
            raise OrchestraError(ErrorCode.REWORK_LOOP, "rework loop detected", details={"signature": signature})
        return signature

