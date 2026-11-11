"""Idempotent, deterministic Organization Bootstrap."""

from __future__ import annotations

from dataclasses import dataclass
import json
import os
from pathlib import Path
import platform
import shutil
import subprocess

from .models import new_id, utc_now
from .storage import SQLiteStore
from .telemetry import Event


@dataclass(frozen=True, slots=True)
class BootstrapStatus:
    project_id: str
    project_name: str
    os: str
    terminal: str
    no_color: bool
    runtimes: dict[str, str | None]
    recoverable_tasks: int
    database: str
    initialized_at: str

    def to_dict(self) -> dict[str, object]:
        return {
            "project_id": self.project_id,
            "project_name": self.project_name,
            "os": self.os,
            "terminal": self.terminal,
            "no_color": self.no_color,
            "runtimes": self.runtimes,
            "recoverable_tasks": self.recoverable_tasks,
            "database": self.database,
            "initialized_at": self.initialized_at,
        }


def _version(command: str, *args: str) -> str | None:
    executable = shutil.which(command)
    if executable is None:
        return None
    try:
        result = subprocess.run([executable, *args], capture_output=True, text=True, timeout=3, check=False)
        line = (result.stdout or result.stderr).strip().splitlines()
        return line[0] if line else "available"
    except (OSError, subprocess.TimeoutExpired):
        return "unavailable-version"


class Bootstrapper:
    def __init__(self, project_root: str | Path):
        self.root = Path(project_root).resolve()
        self.state_dir = self.root / ".orchestra"
        self.identity_path = self.state_dir / "project.json"
        self.db_path = self.state_dir / "orchestra.db"

    def _identity(self) -> dict[str, str]:
        self.state_dir.mkdir(parents=True, exist_ok=True)
        if self.identity_path.exists():
            return json.loads(self.identity_path.read_text(encoding="utf-8"))
        identity = {"project_id": new_id(), "project_name": self.root.name, "created_at": utc_now()}
        temporary = self.identity_path.with_suffix(".tmp")
        temporary.write_text(json.dumps(identity, indent=2, ensure_ascii=False), encoding="utf-8")
        temporary.replace(self.identity_path)
        return identity

    def run(self) -> tuple[BootstrapStatus, SQLiteStore]:
        identity = self._identity()
        store = SQLiteStore(self.db_path)
        store.ensure_project(identity["project_id"], self.root.name)
        term = os.environ.get("TERM") or ("windows-terminal" if os.environ.get("WT_SESSION") else "unknown")
        no_color = bool(os.environ.get("NO_COLOR")) or term.lower() == "dumb"
        runtimes = {
            "python": platform.python_version(),
            "git": _version("git", "--version"),
            "claude": _version("claude", "--version"),
            "node": _version("node", "--version"),
        }
        recoverable = store.recoverable_tasks(identity["project_id"])
        status = BootstrapStatus(
            project_id=identity["project_id"], project_name=identity["project_name"], os=platform.platform(),
            terminal=term, no_color=no_color, runtimes=runtimes, recoverable_tasks=len(recoverable),
            database=str(self.db_path.relative_to(self.root)), initialized_at=utc_now(),
        )
        store.enqueue_event(Event("bootstrap.completed", new_id(), None, status.to_dict()))
        return status, store

