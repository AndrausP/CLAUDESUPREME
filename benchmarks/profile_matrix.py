"""Small deterministic baseline; writes no claims about unobserved token or billing data."""

from __future__ import annotations

import argparse
from datetime import UTC, datetime
import json
from pathlib import Path
import platform
import statistics
from time import perf_counter

from orchestra_core.budgets import PROFILES
from orchestra_core.models import BudgetProfile
from orchestra_core.routing import AgentCapability, Router, TaskSignals


def run(iterations: int) -> dict[str, object]:
    router = Router()
    candidates = [
        AgentCapability("feature-engineer", frozenset({"backend", "tests"})),
        AgentCapability("automated-test-engineer", frozenset({"tests"})),
        AgentCapability("backend-lead", frozenset(), leader=True),
    ]
    profiles: dict[str, object] = {}
    for profile in BudgetProfile:
        samples: list[float] = []
        selected: list[str] = []
        for _ in range(iterations):
            started = perf_counter()
            decision = router.route(TaskSignals(mutation=True), {"backend", "tests"}, candidates)
            samples.append((perf_counter() - started) * 1000)
            selected = [item.id for item in decision.selected_agents]
        profiles[profile.value] = {
            "iterations": iterations,
            "duration_ms_median": statistics.median(samples),
            "duration_ms_min": min(samples),
            "duration_ms_max": max(samples),
            "selected_agents": selected,
            "limits": PROFILES[profile].__dict__ if hasattr(PROFILES[profile], "__dict__") else {
                field: getattr(PROFILES[profile], field)
                for field in PROFILES[profile].__dataclass_fields__
            },
            "tokens": {"value": None, "provenance": "unknown"},
            "cost": {"value": None, "provenance": "unknown"},
        }
    return {
        "schema_version": "1.0.0",
        "observed_at": datetime.now(UTC).isoformat().replace("+00:00", "Z"),
        "environment": {"python": platform.python_version(), "platform": platform.platform()},
        "scenario_a_without_organization": {"status": "not_executed", "reason": "no equivalent non-Orchestra harness in this repository"},
        "profiles": profiles,
        "limitations": ["single host", "routing microbenchmark only", "no model call", "no billing data"],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--iterations", type=int, default=25)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    if args.iterations < 2:
        parser.error("--iterations must be >= 2")
    payload = run(args.iterations)
    rendered = json.dumps(payload, indent=2, ensure_ascii=False)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered + "\n", encoding="utf-8")
    else:
        print(rendered)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

