"""Command-line interface for Orchestra Core.

The CLI is intentionally stdlib-first. Rich and Textual are optional renderers;
all state-changing operations delegate to the deterministic core.
"""

from __future__ import annotations

import argparse
from contextlib import contextmanager
from dataclasses import asdict
from datetime import UTC, datetime
import hashlib
import importlib.util
import json
import locale
import os
from pathlib import Path
import platform
import re
import shutil
import subprocess
import sys
import tempfile
from typing import Any, Callable, Iterator, Sequence
from uuid import uuid4

from .budgets import BudgetGuard, BudgetUsage, PROFILES
from .bootstrap import Bootstrapper
from .errors import ErrorCode, OrchestraError
from .memory import MemoryService
from .models import BudgetProfile, MemoryStatus, MemoryType, TaskRecord, TaskStatus
from .orchestration import OrchestraService
from .registry import RegistryService
from .routing import AgentCapability, Router, TaskSignals
from .storage import SQLiteStore
from .workflow import TransitionRequest
from .adapters.ledger import LedgerAdapter


APP_NAME = "ORCHESTRA CORE"
PACKAGE_VERSION = "0.1.0"
SCHEMA_VERSION = "1.0.0"
TERMINAL_STATUSES = {TaskStatus.COMPLETED, TaskStatus.FAILED, TaskStatus.CANCELLED}
STATUS_TOKENS = {
    TaskStatus.CREATED: "[ ]",
    TaskStatus.CLASSIFIED: "[ ]",
    TaskStatus.PLANNED: "[ ]",
    TaskStatus.READY: "[ ]",
    TaskStatus.RUNNING: "[>]",
    TaskStatus.BLOCKED: "[!]",
    TaskStatus.REVIEWING: "[>]",
    TaskStatus.VALIDATING: "[>]",
    TaskStatus.APPROVED: "[OK]",
    TaskStatus.REWORK_REQUIRED: "[!]",
    TaskStatus.COMPLETED: "[OK]",
    TaskStatus.FAILED: "[X]",
    TaskStatus.CANCELLED: "[-]",
}


def _utc_now() -> str:
    return datetime.now(UTC).isoformat().replace("+00:00", "Z")


def _json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True, default=str)


def _ascii_safe(value: object, encoding: str | None = None) -> str:
    """Return display-safe text without mutating persisted UTF-8 content."""
    text = str(value)
    target = encoding or getattr(sys.stdout, "encoding", None) or locale.getpreferredencoding(False)
    try:
        text.encode(target or "ascii")
        return text
    except (LookupError, UnicodeEncodeError):
        return text.encode("ascii", "replace").decode("ascii")


def _terminal_size() -> os.terminal_size:
    return shutil.get_terminal_size(fallback=(80, 24))


def plain_required(args: argparse.Namespace | None = None) -> bool:
    if args is not None and getattr(args, "plain", False):
        return True
    size = _terminal_size()
    return any(
        (
            os.environ.get("NO_COLOR") is not None,
            os.environ.get("TERM", "").lower() == "dumb",
            os.environ.get("ORCHESTRA_ACCESSIBLE") == "1",
            not getattr(sys.stdout, "isatty", lambda: False)(),
            size.columns < 80,
            size.lines < 24,
        )
    )


def renderer_name(args: argparse.Namespace) -> str:
    if getattr(args, "json_output", False) or getattr(args, "format", None) == "json":
        return "json"
    requested = getattr(args, "format", "auto")
    if requested == "plain" or plain_required(args):
        return "plain"
    if requested in {"auto", "rich"} and importlib.util.find_spec("rich") is not None:
        return "rich"
    return "plain"


def emit(payload: Any, args: argparse.Namespace, *, title: str | None = None) -> None:
    renderer = renderer_name(args)
    if renderer == "json":
        print(_json(payload))
        return
    if renderer == "rich":
        try:
            from rich.console import Console
            from rich.json import JSON
            from rich.panel import Panel

            console = Console(no_color=os.environ.get("NO_COLOR") is not None)
            body = JSON.from_data(payload) if isinstance(payload, (dict, list)) else str(payload)
            console.print(Panel(body, title=title or APP_NAME, border_style="#BAF3DB"))
            return
        except Exception:
            pass
    if title:
        print(_ascii_safe(title))
    if isinstance(payload, dict):
        for key, value in payload.items():
            if isinstance(value, (dict, list)):
                print(_ascii_safe(f"{key}: {_json(value)}"))
            else:
                print(_ascii_safe(f"{key}: {value}"))
    elif isinstance(payload, list):
        if not payload:
            print("(empty)")
        for item in payload:
            print(_ascii_safe(_json(item) if isinstance(item, (dict, list)) else item))
    else:
        print(_ascii_safe(payload))


def _project_root(path: str | Path | None = None) -> Path:
    start = Path(path or os.getcwd()).resolve()
    for candidate in (start, *start.parents):
        if (candidate / ".claude-plugin" / "plugin.json").is_file() or (candidate / "pyproject.toml").is_file():
            return candidate
    return start


def _state_dir(root: Path) -> Path:
    configured = os.environ.get("ORCHESTRA_STATE_DIR")
    return Path(configured).resolve() if configured else root / ".orchestra"


def _ensure_project_state(root: Path) -> dict[str, Any]:
    state_dir = _state_dir(root)
    state_dir.mkdir(parents=True, exist_ok=True)
    project_file = state_dir / "project.json"
    if project_file.is_file():
        try:
            data = json.loads(project_file.read_text(encoding="utf-8"))
            if isinstance(data.get("project_id"), str):
                return data
        except (OSError, json.JSONDecodeError):
            pass
    data = {
        "schema_version": SCHEMA_VERSION,
        "project_id": str(uuid4()),
        "created_at": _utc_now(),
    }
    project_file.write_text(_json(data) + "\n", encoding="utf-8")
    return data


@contextmanager
def open_store(root: Path) -> Iterator[tuple[SQLiteStore, dict[str, Any]]]:
    state = _ensure_project_state(root)
    store = SQLiteStore(_state_dir(root) / "orchestra.db")
    store.ensure_project(state["project_id"], root.name)
    try:
        yield store, state
    finally:
        store.close()


def _read_json(path: Path, default: Any) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return default


def _find_catalog(root: Path, names: Sequence[str]) -> Any:
    for name in names:
        path = root / "catalogs" / name
        if path.is_file():
            data = _read_json(path, None)
            if data is not None:
                return data
    return None


def load_agents(root: Path) -> list[dict[str, Any]]:
    data = _find_catalog(root, ("agents.json", "agent-catalog.json", "organization.json"))
    if isinstance(data, dict):
        for key in ("agents", "items"):
            if isinstance(data.get(key), list):
                return data[key]
    if isinstance(data, list):
        return data
    result: list[dict[str, Any]] = []
    for path in sorted((root / "agents").glob("**/*.md")) if (root / "agents").is_dir() else []:
        text = path.read_text(encoding="utf-8", errors="replace")
        name = re.search(r"(?m)^name:\s*['\"]?([^'\"\n]+)", text)
        description = re.search(r"(?m)^description:\s*['\"]?([^'\"\n]+)", text)
        model = re.search(r"(?m)^model:\s*['\"]?([^'\"\n]+)", text)
        skills = re.search(r"(?m)^skills:\s*\[([^\]]*)\]", text)
        result.append(
            {
                "id": (name.group(1).strip() if name else path.stem),
                "name": (name.group(1).strip() if name else path.stem),
                "description": (description.group(1).strip() if description else "unknown"),
                "model": (model.group(1).strip() if model else "unknown"),
                "department": path.parent.name if path.parent != root / "agents" else "central",
                "skills": [x.strip().strip("'\"") for x in skills.group(1).split(",")] if skills else [],
                "status": "available",
            }
        )
    return result


def load_skills(root: Path) -> list[dict[str, Any]]:
    data = _find_catalog(root, ("skills.json", "skill-catalog.json"))
    if isinstance(data, dict):
        for key in ("skills", "items"):
            if isinstance(data.get(key), list):
                return data[key]
    if isinstance(data, list):
        return data
    result: list[dict[str, Any]] = []
    skills_dir = root / "skills"
    for path in sorted(skills_dir.glob("*/SKILL.md")) if skills_dir.is_dir() else []:
        text = path.read_text(encoding="utf-8", errors="replace")
        name = re.search(r"(?m)^name:\s*['\"]?([^'\"\n]+)", text)
        description = re.search(r"(?m)^description:\s*['\"]?([^'\"\n]+)", text)
        result.append(
            {
                "id": name.group(1).strip() if name else path.parent.name,
                "description": description.group(1).strip() if description else "unknown",
                "ref": str(path.relative_to(root)).replace("\\", "/"),
                "status": "enabled",
            }
        )
    return result


def load_departments(root: Path) -> list[dict[str, Any]]:
    data = _find_catalog(root, ("departments.json", "organization.json", "agents.json"))
    if isinstance(data, dict) and isinstance(data.get("departments"), list):
        return data["departments"]
    agents = load_agents(root)
    grouped: dict[str, list[dict[str, Any]]] = {}
    for agent in agents:
        department = str(agent.get("department", "central"))
        if department == "central":
            continue
        grouped.setdefault(department, []).append(agent)
    return [
        {
            "id": key,
            "leader": next((a.get("id") for a in values if "lead" in str(a.get("id", ""))), "unknown"),
            "available": len(values),
            "tasks": 0,
            "status": "available",
        }
        for key, values in sorted(grouped.items())
    ]


def _agent_capabilities(root: Path) -> list[AgentCapability]:
    candidates: list[AgentCapability] = []
    for item in load_agents(root):
        agent_id = str(item.get("id") or item.get("name") or "unknown")
        raw = item.get("capabilities") or item.get("problems") or item.get("skills") or []
        if isinstance(raw, str):
            raw = [raw]
        capabilities = frozenset(str(value).strip().lower() for value in raw if str(value).strip())
        if not capabilities:
            capabilities = frozenset({agent_id.replace("-", " ")})
        candidates.append(AgentCapability(agent_id, capabilities, "lead" in agent_id))
    return candidates


def command_bootstrap(args: argparse.Namespace) -> int:
    root = _project_root(args.project)
    status, store = Bootstrapper(root).run()
    try:
        payload = {
            "schema_version": SCHEMA_VERSION,
            "organization": "orchestra-core-default",
            "project": root.name,
            "project_id": status.project_id,
            "state": "ready_with_tasks" if status.recoverable_tasks else "ready",
            "recoverable_tasks": status.recoverable_tasks,
            "database": status.database,
            "environment": status.to_dict(),
            "renderer": renderer_name(args),
        }
    finally:
        store.close()
    emit(payload, args, title=APP_NAME)
    return 0


def command_status(args: argparse.Namespace) -> int:
    root = _project_root(args.project)
    with open_store(root) as (store, state):
        active = store.recoverable_tasks(state["project_id"])
        blocked = [task for task in active if task.status is TaskStatus.BLOCKED]
        current = active[-1] if active else None
        payload = {
            "organization": "7 departments / 36 agents",
            "project": root.name,
            "profile": getattr(args, "profile", None) or "BALANCED",
            "state": "ready_with_alerts" if blocked else "ready",
            "active_tasks": len(active),
            "blocked_tasks": len(blocked),
            "active_task": current.task_id if current else None,
            "active_status": current.status.value if current else None,
            "last_operation": current.updated_at if current else "unknown",
            "alerts": ([f"{task.task_id}: blocked" for task in blocked] or []),
        }
    emit(payload, args, title=APP_NAME)
    return 0


def command_task_create(args: argparse.Namespace) -> int:
    root = _project_root(args.project)
    with open_store(root) as (store, state):
        criteria = [{"id": f"AC-{index}", "text": value, "status": "pending"} for index, value in enumerate(args.criteria or [], 1)]
        task = TaskRecord(
            title=args.title,
            objective=args.objective,
            project_id=state["project_id"],
            owner=args.owner,
            acceptance_criteria=criteria,
            budget_profile=BudgetProfile(args.profile),
        )
        created = OrchestraService.with_defaults(store).create_task(task)
    emit(created.to_dict(), args, title="Task created")
    return 0


def command_task_show(args: argparse.Namespace) -> int:
    root = _project_root(args.project)
    with open_store(root) as (store, _):
        task = store.get_task(args.task_id)
        checkpoint = store.latest_checkpoint(args.task_id)
    payload = task.to_dict()
    payload["checkpoint"] = checkpoint
    emit(payload, args, title=f"Task {args.task_id}")
    return 0


def _transition(store: SQLiteStore, task_id: str, target: TaskStatus, args: argparse.Namespace, reason_code: str) -> TaskRecord:
    task = store.get_task(task_id)
    request = TransitionRequest(
        task_id=task.task_id,
        expected_revision=task.revision,
        from_status=task.status,
        to_status=target,
        actor_type="user",
        actor_id=getattr(args, "actor", None) or "cli-user",
        reason_code=reason_code,
        reason=getattr(args, "reason", None) or reason_code.replace("_", " ").lower(),
        evidence_refs=tuple(getattr(args, "evidence", None) or []),
    )
    return OrchestraService.with_defaults(store).transition(request)


def command_task_transition(args: argparse.Namespace) -> int:
    root = _project_root(args.project)
    with open_store(root) as (store, _):
        updated = _transition(store, args.task_id, TaskStatus(args.to), args, args.reason_code)
    emit(updated.to_dict(), args, title="Transition recorded")
    return 0


def command_task_cancel(args: argparse.Namespace) -> int:
    root = _project_root(args.project)
    with open_store(root) as (store, _):
        task = store.get_task(args.task_id)
        checkpoint_id = store.save_checkpoint(
            task.task_id,
            task.status,
            "pre-cancellation",
            {
                "task_snapshot": task.to_dict(),
                "actor": args.actor,
                "reason": args.reason or "cancel requested",
                "evidence_refs": args.evidence or [],
                "safe_to_resume": True,
            },
        )
        updated = _transition(store, args.task_id, TaskStatus.CANCELLED, args, "CANCEL_REQUESTED")
        checkpoint = store.latest_checkpoint(args.task_id)
    payload = updated.to_dict()
    payload["cancellation_evidence"] = {
        "checkpoint_id": checkpoint_id,
        "step": checkpoint["step"],
        "state": checkpoint["state"],
        "payload": checkpoint["payload"],
    }
    emit(payload, args, title="Task cancelled")
    return 0


def command_task_resume(args: argparse.Namespace) -> int:
    root = _project_root(args.project)
    with open_store(root) as (store, _):
        task = store.get_task(args.task_id)
        if task.status in {TaskStatus.FAILED, TaskStatus.CANCELLED}:
            updated = store.create_child_attempt(args.task_id)
            action = "child_attempt_created"
        elif task.status is TaskStatus.BLOCKED:
            updated = _transition(store, args.task_id, TaskStatus.READY, args, "BLOCKER_RESOLVED")
            action = "task_ready"
        else:
            raise OrchestraError(ErrorCode.INVALID_TRANSITION, "resume requires BLOCKED, FAILED, or CANCELLED task")
    payload = updated.to_dict()
    payload["resume_action"] = action
    emit(payload, args, title="Resume prepared")
    return 0


def command_task_criteria(args: argparse.Namespace) -> int:
    root = _project_root(args.project)
    with open_store(root) as (store, _):
        task = store.get_task(args.task_id)
        selected = set(args.pass_id or [])
        criteria = [{**item, "status": "passed" if item.get("id") in selected else item.get("status", "pending")} for item in task.acceptance_criteria]
        updated = store.mark_criteria(task.task_id, criteria, task.revision)
    emit(updated.to_dict(), args, title="Acceptance criteria updated")
    return 0


def command_route(args: argparse.Namespace) -> int:
    root = _project_root(args.project)
    signals = TaskSignals(
        mutation=args.mutation,
        areas=args.areas,
        uncertainty=args.uncertainty,
        security=args.security,
        data_migration=args.data_migration,
        destructive=args.destructive,
        reversible=not args.irreversible,
        external_dependencies=args.external_dependencies,
        validations=args.validations,
    )
    candidates = _agent_capabilities(root)
    if not candidates:
        candidates = [AgentCapability("central-orchestrator", frozenset({"routing"}), leader=True)]
    required = {item.strip().lower() for item in args.capability if item.strip()}
    decision = Router().route(signals, required, candidates)
    payload = {
        "mode": decision.mode.value,
        "risk": decision.risk.value,
        "selected_agents": [item.to_dict() for item in decision.selected_agents],
        "rejected_candidates": [item.to_dict() for item in decision.rejected_candidates],
    }
    emit(payload, args, title="Routing decision")
    return 0


def _run_readonly(command: Sequence[str], cwd: Path, timeout: int = 60) -> dict[str, Any]:
    try:
        process = subprocess.run(command, cwd=cwd, capture_output=True, text=True, timeout=timeout, shell=False)
        return {
            "command": " ".join(command),
            "exit_code": process.returncode,
            "stdout": process.stdout[-4000:],
            "stderr": process.stderr[-4000:],
        }
    except (OSError, subprocess.TimeoutExpired) as exc:
        return {"command": " ".join(command), "exit_code": None, "error": type(exc).__name__}


def command_clareza(args: argparse.Namespace) -> int:
    root = _project_root(args.project)
    target = (root / args.target).resolve() if args.target else root
    if not target.is_relative_to(root):
        raise OrchestraError(ErrorCode.PERMISSION_DENIED, "review target must stay inside project root")
    checks: list[dict[str, Any]] = []
    findings: list[dict[str, Any]] = []
    relative = "." if target == root else str(target.relative_to(root))
    if shutil.which("git") and (root / ".git").exists():
        diff_check = _run_readonly(("git", "diff", "--check", "--", relative), root)
        checks.append({"id": "git-diff-check", **diff_check})
        if diff_check.get("exit_code") not in {0, None}:
            findings.append({
                "finding_id": str(uuid4()), "severity": "medium", "file": relative,
                "location": None, "evidence": "check:git-diff-check",
                "impact": "The diff contains whitespace or conflict-marker errors.",
                "proposed_fix": "Correct the lines reported by git diff --check.", "confidence": "confirmed",
            })
    else:
        checks.append({"id": "git-diff-check", "status": "unavailable", "reason": "not-a-git-repository"})
    if args.depth in {"NORMAL", "HIGH"}:
        tests = root / "tests"
        if tests.is_dir():
            result = _run_readonly((sys.executable, "-m", "unittest", "discover", "-s", "tests"), root, timeout=args.timeout)
            checks.append({"id": "unit-tests", **result})
            if result.get("exit_code") not in {0, None}:
                findings.append({
                    "finding_id": str(uuid4()), "severity": "high", "file": "tests",
                    "location": None, "evidence": "check:unit-tests", "impact": "Automated tests failed.",
                    "proposed_fix": "Investigate the first failing test and rerun the suite.", "confidence": "confirmed",
                })
        else:
            checks.append({"id": "unit-tests", "status": "unavailable", "reason": "tests-directory-missing"})
    specialists: list[dict[str, str]] = []
    if args.depth == "HIGH":
        if args.security:
            specialists.append({"agent_id": "security-architect", "reason_code": "SECURITY_FLAG"})
        if args.architecture:
            specialists.append({"agent_id": "solution-architect", "reason_code": "ARCHITECTURE_FLAG"})
        specialists = specialists[:2]
    failed = any(check.get("exit_code") not in {0, None} for check in checks)
    unavailable = any(check.get("status") == "unavailable" or check.get("exit_code") is None for check in checks)
    verdict = "CHANGES_REQUESTED" if failed else "INCONCLUSIVE" if unavailable else "APPROVED_WITH_NOTES" if findings else "APPROVED"
    payload = {
        "schema_version": SCHEMA_VERSION,
        "review_id": str(uuid4()),
        "task_id": args.task_id,
        "depth": args.depth,
        "scope": [relative],
        "security_requested": args.security,
        "verdict": verdict,
        "findings": findings,
        "specialists": specialists,
        "checks": checks,
        "evidence_refs": [f"check:{check['id']}" for check in checks],
    }
    emit(payload, args, title=f"Clareza {args.depth}")
    return 2 if verdict == "CHANGES_REQUESTED" else 3 if verdict == "INCONCLUSIVE" else 0


def command_agents(args: argparse.Namespace) -> int:
    items = load_agents(_project_root(args.project))
    if args.department:
        items = [item for item in items if item.get("department") == args.department]
    if args.skill:
        items = [item for item in items if args.skill in (item.get("skills") or [])]
    emit({"count": len(items), "agents": items}, args, title="Agents")
    return 0


def command_departments(args: argparse.Namespace) -> int:
    items = load_departments(_project_root(args.project))
    emit({"count": len(items), "departments": items}, args, title="Departments")
    return 0


def command_skills(args: argparse.Namespace) -> int:
    items = load_skills(_project_root(args.project))
    if args.query:
        query = args.query.lower()
        items = [item for item in items if query in _json(item).lower()]
    emit({"count": len(items), "skills": items}, args, title="Skills")
    return 0


def command_memory(args: argparse.Namespace) -> int:
    root = _project_root(args.project)
    with open_store(root) as (store, state):
        if args.memory_command == "search":
            scope = args.scope or f"project:{state['project_id']}"
            items = store.find_memory(scope, args.query, verified_only=args.verified_only)
            payload = {"scope": scope, "count": len(items), "memories": items}
        elif args.memory_command == "status":
            store.update_memory_status(args.memory_id, MemoryStatus(args.status), args.evidence or [])
            payload = {"memory_id": args.memory_id, "status": args.status, "updated": True}
        else:
            service = MemoryService(store)
            memory_id = service.propose(
                memory_type=MemoryType(args.type), scope=args.scope or f"project:{state['project_id']}",
                title=args.title, summary=args.summary, content_ref=args.content_ref,
                origin={"type": "user", "id": "cli-user"}, tags=args.tag or [], evidence_refs=args.evidence or [],
            )
            payload = {"memory_id": memory_id, "status": "PROPOSED"}
    emit(payload, args, title="Memory")
    return 0


def command_budget(args: argparse.Namespace) -> int:
    if args.budget_command == "list":
        payload = {
            "profiles": {
                profile.value: {**asdict(limits), "token_enforcement": "advisory-when-unobserved"}
                for profile, limits in PROFILES.items()
            },
            "safety_minimums": "always",
        }
    else:
        usage = BudgetUsage(
            agent_runs=args.agent_runs, parallel_agents=args.parallel_agents, retries=args.retries,
            rework_cycles=args.rework_cycles, duration_seconds=args.duration_seconds,
            artifact_bytes=args.artifact_bytes, tokens=args.tokens,
        )
        BudgetGuard(BudgetProfile(args.profile)).validate(usage)
        payload = {"profile": args.profile, "within_budget": True, "usage": asdict(usage)}
    emit(payload, args, title="Budget")
    return 0


def command_pipeline(args: argparse.Namespace) -> int:
    root = _project_root(args.project)
    with open_store(root) as (store, _):
        task = store.get_task(args.task_id)
    ordered = ["Planning", "Architecture", "Implementation", "Tests", "Review", "Delivery"]
    active_index = {
        TaskStatus.CREATED: 0, TaskStatus.CLASSIFIED: 0, TaskStatus.PLANNED: 0, TaskStatus.READY: 2,
        TaskStatus.RUNNING: 2, TaskStatus.REVIEWING: 4, TaskStatus.VALIDATING: 3,
        TaskStatus.APPROVED: 5, TaskStatus.COMPLETED: 5, TaskStatus.REWORK_REQUIRED: 2,
        TaskStatus.BLOCKED: 2, TaskStatus.FAILED: 2, TaskStatus.CANCELLED: 2,
    }[task.status]
    stages = []
    for index, name in enumerate(ordered):
        status = "completed" if index < active_index else "running" if index == active_index and task.status not in TERMINAL_STATUSES else "pending"
        if index == active_index and task.status is TaskStatus.BLOCKED:
            status = "blocked"
        elif index == active_index and task.status is TaskStatus.FAILED:
            status = "failed"
        elif index == active_index and task.status is TaskStatus.CANCELLED:
            status = "cancelled"
        elif task.status is TaskStatus.COMPLETED:
            status = "completed"
        stages.append({"name": name, "status": status})
    emit({"task_id": task.task_id, "status": task.status.value, "stages": stages}, args, title="Pipeline")
    return 0


def command_doctor(args: argparse.Namespace) -> int:
    root = _project_root(args.project)
    checks: list[dict[str, Any]] = []
    def check(name: str, status: str, detail: Any) -> None:
        checks.append({"name": name, "status": status, "detail": detail})
    check("python", "ok" if sys.version_info >= (3, 12) else "failed", platform.python_version())
    check("sqlite", "ok", __import__("sqlite3").sqlite_version)
    check("git", "ok" if shutil.which("git") else "warning", shutil.which("git") or "not-found")
    check("claude", "ok" if shutil.which("claude") else "warning", shutil.which("claude") or "not-found")
    check("rich", "ok" if importlib.util.find_spec("rich") else "optional", "installed" if importlib.util.find_spec("rich") else "not-installed")
    check("textual", "ok" if importlib.util.find_spec("textual") else "optional", "installed" if importlib.util.find_spec("textual") else "not-installed")
    check("terminal", "warning" if plain_required(args) else "ok", {
        "term": os.environ.get("TERM", "unknown"), "tty": getattr(sys.stdout, "isatty", lambda: False)(),
        "encoding": getattr(sys.stdout, "encoding", "unknown"), "size": list(_terminal_size()), "renderer": renderer_name(args),
    })
    if args.validate_plugin:
        if shutil.which("claude"):
            result = _run_readonly(("claude", "plugin", "validate", str(root)), root, 120)
            check("plugin", "ok" if result.get("exit_code") == 0 else "failed", result)
        else:
            check("plugin", "warning", "claude-not-found")
    fatal = any(item["status"] == "failed" for item in checks)
    emit({"healthy": not fatal, "checks": checks}, args, title="Doctor")
    return 1 if fatal else 0


def _event_file(root: Path) -> Path:
    return _state_dir(root) / "events.jsonl"


def command_audit(args: argparse.Namespace) -> int:
    root = _project_root(args.project)
    path = Path(args.file).resolve() if args.file else _event_file(root)
    events: list[dict[str, Any]] = []
    if path.is_file():
        for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
            try:
                item = json.loads(line)
            except json.JSONDecodeError:
                continue
            if args.task_id and item.get("task_id") != args.task_id:
                continue
            events.append(item)
    emit({"count": len(events), "events": events[-args.limit:]}, args, title="Audit timeline")
    return 0


def command_report(args: argparse.Namespace) -> int:
    root = _project_root(args.project)
    output = (root / args.output).resolve()
    if not output.is_relative_to(root):
        raise OrchestraError(ErrorCode.PERMISSION_DENIED, "report output must stay inside project root")
    with open_store(root) as (store, _):
        task = store.get_task(args.task_id)
        checkpoint = store.latest_checkpoint(args.task_id)
    report = {"generated_at": _utc_now(), "task": task.to_dict(), "checkpoint": checkpoint}
    output.parent.mkdir(parents=True, exist_ok=True)
    if output.suffix.lower() == ".json":
        output.write_text(_json(report) + "\n", encoding="utf-8")
    else:
        lines = [f"# Task {task.task_id}", "", f"- Status: {task.status.value}", f"- Owner: {task.owner}", f"- Revision: {task.revision}", "", "## Evidence", ""]
        lines.extend(f"- {ref}" for ref in (checkpoint or {}).get("payload", {}).get("evidence_refs", []))
        output.write_text("\n".join(lines) + "\n", encoding="utf-8")
    emit({"report": str(output.relative_to(root)), "written": True}, args, title="Report written")
    return 0


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def command_extension(args: argparse.Namespace) -> int:
    root = _project_root(args.project)
    if args.extension_command == "list":
        payload = {"agents": len(load_agents(root)), "skills": len(load_skills(root)), "status": "local-catalog"}
    elif args.extension_command == "inspect":
        report = RegistryService.analyze(args.path)
        payload = {
            "status": "quarantined", "executed": False, "checksum": report.checksum,
            "files": report.files, "bytes": report.bytes,
            "executable_candidates": list(report.executable_candidates), "warnings": list(report.warnings),
        }
    else:
        with open_store(root) as (store, _):
            registry = RegistryService(store)
            if args.extension_command == "add":
                report = registry.register(
                    component_id=args.component_id, version=args.version, component_type=args.type,
                    origin_kind=args.origin_kind, origin_uri=args.origin_uri or args.path,
                    path=args.path, description=args.description,
                )
                payload = {
                    "component_id": args.component_id, "status": "quarantined" if args.origin_kind != "local" else "disabled",
                    "checksum": report.checksum, "executed": False, "warnings": list(report.warnings),
                }
            elif args.extension_command in {"disable", "remove", "enable"}:
                target_status = {"disable": "disabled", "remove": "removed", "enable": "enabled"}[args.extension_command]
                registry.set_status(args.component, target_status, expected_checksum=args.checksum, external_confirmation=args.confirm)
                payload = {"component_id": args.component, "status": target_status, "updated": True}
            elif args.extension_command == "export":
                output = (root / args.output).resolve()
                if not output.is_relative_to(root):
                    raise OrchestraError(ErrorCode.PERMISSION_DENIED, "extension export must stay inside project root")
                output.parent.mkdir(parents=True, exist_ok=True)
                registry.export_record(args.component, output)
                payload = {"component_id": args.component, "export": str(output.relative_to(root)), "written": True}
            else:
                raise OrchestraError(ErrorCode.INVALID_SCHEMA, f"unsupported extension command: {args.extension_command}")
    emit(payload, args, title="Extension")
    return 0


def _organization_manifest(root: Path) -> dict[str, Any]:
    agents = load_agents(root)
    skills = load_skills(root)
    departments = load_departments(root)
    return {
        "schema_version": SCHEMA_VERSION,
        "organization_id": "orchestra-core-default",
        "protocol_version": SCHEMA_VERSION,
        "package_version": PACKAGE_VERSION,
        "generated_at": _utc_now(),
        "departments": departments,
        "agents": [{"id": item.get("id"), "enabled": item.get("status", "available") != "disabled", "ref": item.get("ref")} for item in agents],
        "skills": [{"id": item.get("id"), "ref": item.get("ref")} for item in skills],
        "mcp_servers": [],
        "profiles": [profile.value for profile in BudgetProfile],
        "policies": [{"id": "least-privilege", "version": SCHEMA_VERSION}],
        "dependencies": [],
        "integrations": {"claude_code": "available" if shutil.which("claude") else "unknown", "claude_ledger": "optional"},
        "checksums": {},
    }


def command_ledger_export(args: argparse.Namespace) -> int:
    root = _project_root(args.project)
    output = (root / args.output).resolve()
    if not output.is_relative_to(root):
        raise OrchestraError(ErrorCode.PERMISSION_DENIED, "ledger export must stay inside project root")
    output.mkdir(parents=True, exist_ok=True)
    manifest_path = output / "organization.manifest.json"
    with open_store(root) as (store, _):
        adapter = LedgerAdapter(store)
        adapter.write_manifest(
            manifest_path,
            departments=load_departments(root),
            agents=load_agents(root),
            skills=load_skills(root),
        )
        exported = adapter.export_events(output / "events.jsonl")
    emit({"manifest": str(manifest_path.relative_to(root)), "events_exported": exported, "ledger_required": False}, args, title="Ledger export")
    return 0


def command_tui(args: argparse.Namespace) -> int:
    from .tui import launch_tui
    root = _project_root(args.project)
    if launch_tui(root, force=args.force):
        return 0
    args.plain = True
    return command_status(args)


def add_global_options(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--project", help="Project root (default: auto-detect from cwd)")
    parser.add_argument("--json", dest="json_output", action="store_true", help="Emit stable JSON on stdout")
    parser.add_argument("--plain", action="store_true", help="Force dependency-free ASCII output")
    parser.add_argument("--format", choices=("auto", "plain", "rich", "json"), default="auto")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="orchestra", description="Local-first control plane for specialized Claude Code agents")
    parser.add_argument("--version", action="version", version=f"%(prog)s {PACKAGE_VERSION}")
    add_global_options(parser)
    sub = parser.add_subparsers(dest="command")

    status = sub.add_parser("status", help="Show organization and active task status")
    status.add_argument("--profile", choices=[item.value for item in BudgetProfile], default="BALANCED")
    status.set_defaults(handler=command_status)
    bootstrap = sub.add_parser("bootstrap", help="Initialize and reconcile local state idempotently")
    bootstrap.set_defaults(handler=command_bootstrap)

    task = sub.add_parser("task", help="Create and manage workflow tasks")
    task_sub = task.add_subparsers(dest="task_command", required=True)
    create = task_sub.add_parser("create")
    create.add_argument("title")
    create.add_argument("--objective", required=True)
    create.add_argument("--owner", default="central-orchestrator")
    create.add_argument("--criteria", action="append")
    create.add_argument("--profile", choices=[item.value for item in BudgetProfile], default="BALANCED")
    create.set_defaults(handler=command_task_create)
    show = task_sub.add_parser("show")
    show.add_argument("task_id")
    show.set_defaults(handler=command_task_show)
    transition = task_sub.add_parser("transition")
    transition.add_argument("task_id")
    transition.add_argument("to", choices=[item.value for item in TaskStatus])
    transition.add_argument("--actor", default="cli-user")
    transition.add_argument("--reason-code", default="MANUAL_TRANSITION")
    transition.add_argument("--reason")
    transition.add_argument("--evidence", action="append")
    transition.set_defaults(handler=command_task_transition)
    resume = task_sub.add_parser("resume")
    resume.add_argument("task_id")
    resume.add_argument("--actor", default="cli-user")
    resume.add_argument("--reason")
    resume.set_defaults(handler=command_task_resume)
    cancel = task_sub.add_parser("cancel")
    cancel.add_argument("task_id")
    cancel.add_argument("--actor", default="cli-user")
    cancel.add_argument("--reason")
    cancel.add_argument("--evidence", action="append")
    cancel.set_defaults(handler=command_task_cancel)
    criteria = task_sub.add_parser("criteria")
    criteria.add_argument("task_id")
    criteria.add_argument("--pass", dest="pass_id", action="append", required=True)
    criteria.set_defaults(handler=command_task_criteria)

    route = sub.add_parser("route", help="Classify a task and select the minimum sufficient agents")
    route.add_argument("--capability", action="append", default=[])
    route.add_argument("--mutation", action="store_true")
    route.add_argument("--areas", type=int, default=1)
    route.add_argument("--uncertainty", type=int, default=0)
    route.add_argument("--security", action="store_true")
    route.add_argument("--data-migration", action="store_true")
    route.add_argument("--destructive", action="store_true")
    route.add_argument("--irreversible", action="store_true")
    route.add_argument("--external-dependencies", type=int, default=0)
    route.add_argument("--validations", type=int, default=1)
    route.set_defaults(handler=command_route)

    clareza = sub.add_parser("clareza", help="Evidence-based QUICK, NORMAL, or HIGH review")
    clareza.add_argument("depth", nargs="?", choices=("QUICK", "NORMAL", "HIGH"), default="NORMAL")
    clareza.add_argument("target", nargs="?", default=".")
    clareza.add_argument("--task-id")
    clareza.add_argument("--security", action="store_true")
    clareza.add_argument("--architecture", action="store_true")
    clareza.add_argument("--timeout", type=int, default=120)
    clareza.set_defaults(handler=command_clareza)

    agents = sub.add_parser("agents")
    agents.add_argument("--department")
    agents.add_argument("--skill")
    agents.set_defaults(handler=command_agents)
    departments = sub.add_parser("departments")
    departments.set_defaults(handler=command_departments)
    skills = sub.add_parser("skills", aliases=["components"])
    skills.add_argument("--query")
    skills.set_defaults(handler=command_skills)

    memory = sub.add_parser("memory")
    memory_sub = memory.add_subparsers(dest="memory_command", required=True)
    memory_search = memory_sub.add_parser("search")
    memory_search.add_argument("query")
    memory_search.add_argument("--scope")
    memory_search.add_argument("--verified-only", action="store_true")
    memory_search.set_defaults(handler=command_memory)
    memory_propose = memory_sub.add_parser("propose")
    memory_propose.add_argument("--type", choices=[item.value for item in MemoryType], required=True)
    memory_propose.add_argument("--scope")
    memory_propose.add_argument("--title", required=True)
    memory_propose.add_argument("--summary", required=True)
    memory_propose.add_argument("--content-ref", required=True)
    memory_propose.add_argument("--tag", action="append")
    memory_propose.add_argument("--evidence", action="append")
    memory_propose.set_defaults(handler=command_memory)
    memory_status = memory_sub.add_parser("status")
    memory_status.add_argument("memory_id")
    memory_status.add_argument("status", choices=[item.value for item in MemoryStatus])
    memory_status.add_argument("--evidence", action="append")
    memory_status.set_defaults(handler=command_memory)

    budget = sub.add_parser("budget")
    budget_sub = budget.add_subparsers(dest="budget_command", required=True)
    budget_list = budget_sub.add_parser("list")
    budget_list.set_defaults(handler=command_budget)
    budget_check = budget_sub.add_parser("check")
    budget_check.add_argument("profile", choices=[item.value for item in BudgetProfile])
    budget_check.add_argument("--agent-runs", type=int, default=0)
    budget_check.add_argument("--parallel-agents", type=int, default=0)
    budget_check.add_argument("--retries", type=int, default=0)
    budget_check.add_argument("--rework-cycles", type=int, default=0)
    budget_check.add_argument("--duration-seconds", type=float, default=0)
    budget_check.add_argument("--artifact-bytes", type=int, default=0)
    budget_check.add_argument("--tokens", type=int)
    budget_check.set_defaults(handler=command_budget)

    pipeline = sub.add_parser("pipeline")
    pipeline.add_argument("task_id")
    pipeline.set_defaults(handler=command_pipeline)
    doctor = sub.add_parser("doctor")
    doctor.add_argument("--validate-plugin", action="store_true")
    doctor.set_defaults(handler=command_doctor)
    audit = sub.add_parser("audit")
    audit.add_argument("--task-id")
    audit.add_argument("--file")
    audit.add_argument("--limit", type=int, default=100)
    audit.set_defaults(handler=command_audit)
    report = sub.add_parser("report")
    report.add_argument("task_id")
    report.add_argument("--output", required=True)
    report.set_defaults(handler=command_report)

    extension = sub.add_parser("extension")
    extension_sub = extension.add_subparsers(dest="extension_command", required=True)
    ext_list = extension_sub.add_parser("list")
    ext_list.set_defaults(handler=command_extension)
    ext_inspect = extension_sub.add_parser("inspect")
    ext_inspect.add_argument("path")
    ext_inspect.set_defaults(handler=command_extension)
    ext_add = extension_sub.add_parser("add")
    ext_add.add_argument("path")
    ext_add.add_argument("--id", dest="component_id", required=True)
    ext_add.add_argument("--version", default="0.0.0")
    ext_add.add_argument("--type", choices=("agent", "department", "skill", "mcp", "command", "hook", "validator", "workflow", "storage-provider"), required=True)
    ext_add.add_argument("--origin-kind", choices=("local", "external"), default="local")
    ext_add.add_argument("--origin-uri")
    ext_add.add_argument("--description", required=True)
    ext_add.set_defaults(handler=command_extension)
    for name in ("disable", "remove", "enable"):
        ext = extension_sub.add_parser(name)
        ext.add_argument("component")
        ext.add_argument("--checksum", required=True)
        ext.add_argument("--confirm", action="store_true", help="External confirmation for enable/remove")
        ext.set_defaults(handler=command_extension)
    ext_export = extension_sub.add_parser("export")
    ext_export.add_argument("component")
    ext_export.add_argument("--output", required=True)
    ext_export.set_defaults(handler=command_extension)

    ledger = sub.add_parser("ledger")
    ledger_sub = ledger.add_subparsers(dest="ledger_command", required=True)
    ledger_export = ledger_sub.add_parser("export")
    ledger_export.add_argument("--output", default="integrations/claude-ledger/out")
    ledger_export.set_defaults(handler=command_ledger_export)
    tui = sub.add_parser("tui")
    tui.add_argument("--force", action="store_true", help="Try Textual even when terminal detection recommends plain")
    tui.set_defaults(handler=command_tui)
    return parser


def _normalize_global_options(argv: Sequence[str]) -> list[str]:
    """Allow global options before or after subcommands without custom argparse."""
    values = list(argv)
    options_with_value = {"--project", "--format"}
    flags = {"--json", "--plain"}
    prefix: list[str] = []
    rest: list[str] = []
    index = 0
    while index < len(values):
        value = values[index]
        if value in flags:
            prefix.append(value)
        elif value in options_with_value and index + 1 < len(values):
            prefix.extend((value, values[index + 1]))
            index += 1
        elif any(value.startswith(option + "=") for option in options_with_value):
            prefix.append(value)
        else:
            rest.append(value)
        index += 1
    return prefix + rest


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    raw = list(sys.argv[1:] if argv is None else argv)
    args = parser.parse_args(_normalize_global_options(raw))
    if not args.command:
        args.command = "status"
        args.handler = command_status
        args.profile = "BALANCED"
    try:
        return int(args.handler(args))
    except OrchestraError as exc:
        if getattr(args, "json_output", False) or getattr(args, "format", None) == "json":
            print(_json(exc.to_dict()))
        else:
            print(_ascii_safe(f"ERROR [{exc.code.value}] {exc.message}"), file=sys.stderr)
            if exc.details:
                print(_ascii_safe(_json(exc.details)), file=sys.stderr)
        return 2
    except KeyboardInterrupt:
        print("Cancelled by user.", file=sys.stderr)
        return 130


if __name__ == "__main__":
    raise SystemExit(main())
