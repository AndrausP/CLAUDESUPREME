"""SQLite source of truth with transactional outbox and optimistic locking."""

from __future__ import annotations

from contextlib import contextmanager
from dataclasses import replace
import json
from pathlib import Path
import sqlite3
from threading import RLock
from typing import Any, Iterator

from .errors import ErrorCode, OrchestraError
from .models import (
    BudgetProfile,
    CandidateDecision,
    MemoryStatus,
    MemoryType,
    RiskLevel,
    RoutingMode,
    TaskRecord,
    TaskStatus,
    new_id,
    utc_now,
)
from .sanitize import canonical_json, digest, sanitize
from .telemetry import Event
from .workflow import StateMachine, TransitionRequest


SCHEMA_VERSION = 1


class SQLiteStore:
    def __init__(self, path: str | Path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._lock = RLock()
        self.connection = sqlite3.connect(self.path, timeout=5, isolation_level=None, check_same_thread=False)
        self.connection.row_factory = sqlite3.Row
        self.connection.execute("PRAGMA foreign_keys=ON")
        self.connection.execute("PRAGMA busy_timeout=5000")
        try:
            self.connection.execute("PRAGMA journal_mode=WAL")
        except sqlite3.OperationalError:
            # In-memory and restricted filesystems may not support WAL.
            pass
        self._migrate()

    def close(self) -> None:
        self.connection.close()

    @contextmanager
    def transaction(self) -> Iterator[sqlite3.Connection]:
        with self._lock:
            try:
                self.connection.execute("BEGIN IMMEDIATE")
                yield self.connection
                self.connection.execute("COMMIT")
            except Exception:
                self.connection.execute("ROLLBACK")
                raise

    def _migrate(self) -> None:
        version = int(self.connection.execute("PRAGMA user_version").fetchone()[0])
        if version > SCHEMA_VERSION:
            raise OrchestraError(ErrorCode.INCOMPATIBLE_VERSION, f"database version {version} is newer than supported {SCHEMA_VERSION}")
        if version == 0:
            with self._lock:
                self.connection.executescript(
                    """
                    BEGIN IMMEDIATE;
                    CREATE TABLE projects (
                        project_id TEXT PRIMARY KEY,
                        root_hint TEXT NOT NULL,
                        created_at TEXT NOT NULL,
                        updated_at TEXT NOT NULL
                    );
                    CREATE TABLE tasks (
                        task_id TEXT PRIMARY KEY,
                        parent_task_id TEXT,
                        attempt_of TEXT,
                        project_id TEXT NOT NULL,
                        correlation_id TEXT NOT NULL,
                        title TEXT NOT NULL,
                        objective TEXT NOT NULL,
                        mode TEXT NOT NULL,
                        risk TEXT NOT NULL,
                        status TEXT NOT NULL,
                        owner TEXT NOT NULL,
                        selected_agents_json TEXT NOT NULL,
                        rejected_candidates_json TEXT NOT NULL,
                        acceptance_criteria_json TEXT NOT NULL,
                        dependencies_json TEXT NOT NULL,
                        budget_profile TEXT NOT NULL,
                        revision INTEGER NOT NULL,
                        created_at TEXT NOT NULL,
                        updated_at TEXT NOT NULL,
                        FOREIGN KEY(project_id) REFERENCES projects(project_id)
                    );
                    CREATE TABLE transitions (
                        transition_id TEXT PRIMARY KEY,
                        task_id TEXT NOT NULL,
                        expected_revision INTEGER NOT NULL,
                        from_status TEXT NOT NULL,
                        to_status TEXT NOT NULL,
                        actor_type TEXT NOT NULL,
                        actor_id TEXT NOT NULL,
                        reason_code TEXT NOT NULL,
                        reason TEXT NOT NULL,
                        evidence_refs_json TEXT NOT NULL,
                        occurred_at TEXT NOT NULL,
                        FOREIGN KEY(task_id) REFERENCES tasks(task_id)
                    );
                    CREATE TABLE checkpoints (
                        checkpoint_id TEXT PRIMARY KEY,
                        task_id TEXT NOT NULL,
                        attempt INTEGER NOT NULL,
                        state TEXT NOT NULL,
                        step TEXT NOT NULL,
                        payload_json TEXT NOT NULL,
                        resume_after TEXT,
                        created_at TEXT NOT NULL,
                        FOREIGN KEY(task_id) REFERENCES tasks(task_id)
                    );
                    CREATE TABLE memories (
                        memory_id TEXT PRIMARY KEY,
                        type TEXT NOT NULL,
                        scope TEXT NOT NULL,
                        canonical_key TEXT NOT NULL,
                        title TEXT NOT NULL,
                        summary TEXT NOT NULL,
                        content_ref TEXT NOT NULL,
                        origin_json TEXT NOT NULL,
                        status TEXT NOT NULL,
                        confidence TEXT NOT NULL,
                        tags_json TEXT NOT NULL,
                        relations_json TEXT NOT NULL,
                        evidence_refs_json TEXT NOT NULL,
                        content_sha256 TEXT NOT NULL,
                        revision INTEGER NOT NULL,
                        created_at TEXT NOT NULL,
                        last_validated_at TEXT,
                        UNIQUE(scope, canonical_key, content_sha256)
                    );
                    CREATE TABLE components (
                        component_id TEXT PRIMARY KEY,
                        version TEXT NOT NULL,
                        type TEXT NOT NULL,
                        origin_json TEXT NOT NULL,
                        description TEXT NOT NULL,
                        permissions_json TEXT NOT NULL,
                        dependencies_json TEXT NOT NULL,
                        compatibility_json TEXT NOT NULL,
                        status TEXT NOT NULL,
                        checksum TEXT NOT NULL,
                        configuration_ref TEXT,
                        updated_at TEXT NOT NULL
                    );
                    CREATE TABLE event_outbox (
                        sequence INTEGER PRIMARY KEY AUTOINCREMENT,
                        event_id TEXT UNIQUE NOT NULL,
                        event_json TEXT NOT NULL,
                        exported_at TEXT
                    );
                    CREATE INDEX idx_tasks_project_status ON tasks(project_id, status);
                    CREATE INDEX idx_memory_search ON memories(scope, status, title, summary);
                    CREATE INDEX idx_outbox_pending ON event_outbox(exported_at, sequence);
                    PRAGMA user_version=1;
                    COMMIT;
                    """
                )

    def ensure_project(self, project_id: str, root_hint: str) -> None:
        now = utc_now()
        with self.transaction() as conn:
            conn.execute(
                "INSERT INTO projects(project_id,root_hint,created_at,updated_at) VALUES(?,?,?,?) "
                "ON CONFLICT(project_id) DO UPDATE SET root_hint=excluded.root_hint,updated_at=excluded.updated_at",
                (project_id, root_hint, now, now),
            )

    def create_task(self, task: TaskRecord) -> TaskRecord:
        with self.transaction() as conn:
            conn.execute(
                """INSERT INTO tasks VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                (
                    task.task_id, task.parent_task_id, task.attempt_of, task.project_id, task.correlation_id,
                    task.title, task.objective, task.mode.value, task.risk.value, task.status.value, task.owner,
                    canonical_json([item.to_dict() for item in task.selected_agents]),
                    canonical_json([item.to_dict() for item in task.rejected_candidates]),
                    canonical_json(task.acceptance_criteria), canonical_json(task.dependencies),
                    task.budget_profile.value, task.revision, task.created_at, task.updated_at,
                ),
            )
            self._enqueue(conn, Event("task.created", task.correlation_id, task.task_id, {"title": task.title, "owner": task.owner}))
        return task

    def get_task(self, task_id: str) -> TaskRecord:
        row = self.connection.execute("SELECT * FROM tasks WHERE task_id=?", (task_id,)).fetchone()
        if row is None:
            raise OrchestraError(ErrorCode.NOT_FOUND, f"task not found: {task_id}")
        return self._task_from_row(row)

    def _task_from_row(self, row: sqlite3.Row) -> TaskRecord:
        return TaskRecord(
            task_id=row["task_id"], parent_task_id=row["parent_task_id"], attempt_of=row["attempt_of"],
            project_id=row["project_id"], correlation_id=row["correlation_id"], title=row["title"],
            objective=row["objective"], mode=RoutingMode(row["mode"]), risk=RiskLevel(row["risk"]),
            status=TaskStatus(row["status"]), owner=row["owner"],
            selected_agents=[CandidateDecision(**item) for item in json.loads(row["selected_agents_json"])],
            rejected_candidates=[CandidateDecision(**item) for item in json.loads(row["rejected_candidates_json"])],
            acceptance_criteria=json.loads(row["acceptance_criteria_json"]),
            dependencies=json.loads(row["dependencies_json"]), budget_profile=BudgetProfile(row["budget_profile"]),
            revision=row["revision"], created_at=row["created_at"], updated_at=row["updated_at"],
        )

    def transition(self, request: TransitionRequest) -> TaskRecord:
        with self.transaction() as conn:
            row = conn.execute("SELECT * FROM tasks WHERE task_id=?", (request.task_id,)).fetchone()
            if row is None:
                raise OrchestraError(ErrorCode.NOT_FOUND, f"task not found: {request.task_id}")
            current = self._task_from_row(row)
            if current.revision != request.expected_revision or current.status is not request.from_status:
                raise OrchestraError(
                    ErrorCode.REVISION_CONFLICT,
                    "task changed before transition",
                    details={"expected_revision": request.expected_revision, "actual_revision": current.revision, "actual_status": current.status.value},
                    correlation_id=current.correlation_id,
                )
            StateMachine.validate(request, current.acceptance_criteria)
            if request.to_status is TaskStatus.RUNNING and current.dependencies:
                dependency_ids = list(dict.fromkeys(current.dependencies))
                placeholders = ",".join("?" for _ in dependency_ids)
                dependency_rows = conn.execute(
                    f"SELECT task_id,status FROM tasks WHERE task_id IN ({placeholders})",
                    dependency_ids,
                ).fetchall()
                dependency_statuses = {row["task_id"]: row["status"] for row in dependency_rows}
                blocked_dependencies = [
                    {
                        "task_id": dependency_id,
                        "status": dependency_statuses.get(dependency_id, "NOT_FOUND"),
                    }
                    for dependency_id in dependency_ids
                    if dependency_statuses.get(dependency_id) != TaskStatus.COMPLETED.value
                ]
                if blocked_dependencies:
                    raise OrchestraError(
                        ErrorCode.DEPENDENCY_BLOCKED,
                        "task dependencies must be completed before RUNNING",
                        details={
                            "task_id": current.task_id,
                            "blocked_dependencies": blocked_dependencies,
                        },
                        correlation_id=current.correlation_id,
                    )
            now = utc_now()
            revision = current.revision + 1
            updated = conn.execute(
                "UPDATE tasks SET status=?,revision=?,updated_at=? WHERE task_id=? AND revision=?",
                (request.to_status.value, revision, now, current.task_id, current.revision),
            )
            if updated.rowcount != 1:
                raise OrchestraError(ErrorCode.REVISION_CONFLICT, "optimistic update failed")
            transition_id = new_id()
            conn.execute(
                "INSERT INTO transitions VALUES(?,?,?,?,?,?,?,?,?,?,?)",
                (transition_id, current.task_id, current.revision, current.status.value, request.to_status.value,
                 request.actor_type, request.actor_id, request.reason_code, request.reason,
                 canonical_json(list(request.evidence_refs)), now),
            )
            event_type = "task.completed" if request.to_status is TaskStatus.COMPLETED else "task.failed" if request.to_status is TaskStatus.FAILED else "task.transitioned"
            self._enqueue(conn, Event(event_type, current.correlation_id, current.task_id, {
                "transition_id": transition_id, "from": current.status.value, "to": request.to_status.value,
                "reason_code": request.reason_code, "evidence_refs": list(request.evidence_refs),
            }))
        return replace(current, status=request.to_status, revision=revision, updated_at=now)

    def update_task_classification(
        self,
        task_id: str,
        expected_revision: int,
        mode: RoutingMode,
        risk: RiskLevel,
        selected: list[CandidateDecision],
        rejected: list[CandidateDecision],
    ) -> TaskRecord:
        with self.transaction() as conn:
            row = conn.execute("SELECT * FROM tasks WHERE task_id=?", (task_id,)).fetchone()
            if row is None:
                raise OrchestraError(ErrorCode.NOT_FOUND, f"task not found: {task_id}")
            task = self._task_from_row(row)
            if task.revision != expected_revision or task.status is not TaskStatus.CREATED:
                raise OrchestraError(ErrorCode.REVISION_CONFLICT, "classification revision conflict")
            now = utc_now()
            revision = task.revision + 1
            conn.execute(
                "UPDATE tasks SET mode=?,risk=?,status=?,selected_agents_json=?,rejected_candidates_json=?,revision=?,updated_at=? WHERE task_id=? AND revision=?",
                (mode.value, risk.value, TaskStatus.CLASSIFIED.value, canonical_json([x.to_dict() for x in selected]),
                 canonical_json([x.to_dict() for x in rejected]), revision, now, task_id, expected_revision),
            )
            conn.execute(
                "INSERT INTO transitions VALUES(?,?,?,?,?,?,?,?,?,?,?)",
                (new_id(), task.task_id, expected_revision, TaskStatus.CREATED.value, TaskStatus.CLASSIFIED.value,
                 "system", "router", "TASK_CLASSIFIED", "Deterministic routing completed", "[]", now),
            )
            self._enqueue(conn, Event("task.classified", task.correlation_id, task.task_id, {
                "mode": mode.value, "risk": risk.value,
                "selected_agents": [x.to_dict() for x in selected], "rejected_candidates": [x.to_dict() for x in rejected],
            }))
        return replace(task, mode=mode, risk=risk, status=TaskStatus.CLASSIFIED, selected_agents=selected, rejected_candidates=rejected, revision=revision, updated_at=now)

    def mark_criteria(self, task_id: str, criteria: list[dict[str, Any]], expected_revision: int) -> TaskRecord:
        with self.transaction() as conn:
            row = conn.execute("SELECT * FROM tasks WHERE task_id=?", (task_id,)).fetchone()
            if row is None:
                raise OrchestraError(ErrorCode.NOT_FOUND, f"task not found: {task_id}")
            task = self._task_from_row(row)
            if task.revision != expected_revision:
                raise OrchestraError(ErrorCode.REVISION_CONFLICT, "criteria revision conflict")
            now = utc_now()
            conn.execute("UPDATE tasks SET acceptance_criteria_json=?,revision=revision+1,updated_at=? WHERE task_id=? AND revision=?", (canonical_json(criteria), now, task_id, expected_revision))
        return replace(task, acceptance_criteria=criteria, revision=expected_revision + 1, updated_at=now)

    def save_checkpoint(self, task_id: str, state: TaskStatus, step: str, payload: dict[str, Any], *, attempt: int = 1, resume_after: str | None = None) -> str:
        checkpoint_id = new_id()
        with self.transaction() as conn:
            conn.execute(
                "INSERT INTO checkpoints VALUES(?,?,?,?,?,?,?,?)",
                (checkpoint_id, task_id, attempt, state.value, step, canonical_json(sanitize(payload)), resume_after, utc_now()),
            )
        return checkpoint_id

    def latest_checkpoint(self, task_id: str) -> dict[str, Any] | None:
        row = self.connection.execute("SELECT * FROM checkpoints WHERE task_id=? ORDER BY created_at DESC LIMIT 1", (task_id,)).fetchone()
        if row is None:
            return None
        return {**dict(row), "payload": json.loads(row["payload_json"])}

    def recoverable_tasks(self, project_id: str) -> list[TaskRecord]:
        terminal = tuple(state.value for state in (TaskStatus.COMPLETED, TaskStatus.FAILED, TaskStatus.CANCELLED))
        rows = self.connection.execute(
            f"SELECT * FROM tasks WHERE project_id=? AND status NOT IN ({','.join('?' for _ in terminal)}) ORDER BY updated_at",
            (project_id, *terminal),
        ).fetchall()
        return [self._task_from_row(row) for row in rows]

    def create_child_attempt(self, task_id: str) -> TaskRecord:
        parent = self.get_task(task_id)
        if parent.status not in {TaskStatus.FAILED, TaskStatus.CANCELLED}:
            raise OrchestraError(ErrorCode.INVALID_TRANSITION, "only terminal failed/cancelled tasks can create attempts")
        child = replace(parent, task_id=new_id(), parent_task_id=parent.task_id, attempt_of=parent.attempt_of or parent.task_id,
                        correlation_id=new_id(), status=TaskStatus.CREATED, revision=0, created_at=utc_now(), updated_at=utc_now())
        return self.create_task(child)

    def _enqueue(self, conn: sqlite3.Connection, event: Event) -> None:
        raw = event.to_dict()
        conn.execute("INSERT INTO event_outbox(event_id,event_json) VALUES(?,?)", (event.event_id, canonical_json(raw)))

    def enqueue_event(self, event: Event) -> None:
        with self.transaction() as conn:
            self._enqueue(conn, event)

    def export_events(self, destination: str | Path) -> int:
        path = Path(destination)
        path.parent.mkdir(parents=True, exist_ok=True)
        existing_ids: set[str] = set()
        if path.exists():
            for line in path.read_text(encoding="utf-8").splitlines():
                try:
                    existing_ids.add(json.loads(line)["event_id"])
                except (json.JSONDecodeError, KeyError):
                    continue
        rows = self.connection.execute("SELECT sequence,event_id,event_json FROM event_outbox WHERE exported_at IS NULL ORDER BY sequence").fetchall()
        if not rows:
            return 0
        lines: list[str] = []
        for row in rows:
            event = json.loads(row["event_json"])
            event["sequence"] = row["sequence"]
            if row["event_id"] not in existing_ids:
                lines.append(canonical_json(event))
        if lines:
            with path.open("a", encoding="utf-8", newline="\n") as handle:
                for line in lines:
                    handle.write(line + "\n")
        with self.transaction() as conn:
            conn.executemany("UPDATE event_outbox SET exported_at=? WHERE event_id=?", [(utc_now(), row["event_id"]) for row in rows])
        return len(lines)

    # Memory persistence primitives used by MemoryService.
    def insert_memory(self, record: dict[str, Any]) -> str:
        with self.transaction() as conn:
            try:
                conn.execute(
                    "INSERT INTO memories VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                    (record["memory_id"], record["type"], record["scope"], record["canonical_key"], record["title"],
                     record["summary"], record["content_ref"], canonical_json(record["origin"]), record["status"],
                     record["confidence"], canonical_json(record["tags"]), canonical_json(record["relations"]),
                     canonical_json(record["evidence_refs"]), record["content_sha256"], record["revision"],
                     record["created_at"], record.get("last_validated_at")),
                )
                self._enqueue(conn, Event("memory.proposed", record["origin"].get("id", new_id()), None, {
                    "memory_id": record["memory_id"], "type": record["type"], "scope": record["scope"],
                }))
            except sqlite3.IntegrityError as exc:
                raise OrchestraError(ErrorCode.INVALID_SCHEMA, "duplicate memory", details={"scope": record["scope"], "canonical_key": record["canonical_key"]}) from exc
        return record["memory_id"]

    def find_memory(self, scope: str, query: str, *, verified_only: bool = False) -> list[dict[str, Any]]:
        pattern = f"%{query.lower()}%"
        sql = "SELECT * FROM memories WHERE scope=? AND (lower(title) LIKE ? OR lower(summary) LIKE ? OR lower(tags_json) LIKE ?)"
        params: list[Any] = [scope, pattern, pattern, pattern]
        if verified_only:
            sql += " AND status=?"
            params.append(MemoryStatus.VERIFIED.value)
        sql += " ORDER BY created_at DESC"
        return [dict(row) for row in self.connection.execute(sql, params).fetchall()]

    def update_memory_status(self, memory_id: str, status: MemoryStatus, evidence_refs: list[str]) -> None:
        if status is MemoryStatus.VERIFIED and not evidence_refs:
            raise OrchestraError(ErrorCode.VALIDATION_INCONCLUSIVE, "verified memory requires evidence")
        with self.transaction() as conn:
            result = conn.execute(
                "UPDATE memories SET status=?,evidence_refs_json=?,last_validated_at=?,revision=revision+1 WHERE memory_id=?",
                (status.value, canonical_json(evidence_refs), utc_now(), memory_id),
            )
            if result.rowcount != 1:
                raise OrchestraError(ErrorCode.NOT_FOUND, f"memory not found: {memory_id}")

    def upsert_component(self, record: dict[str, Any]) -> None:
        with self.transaction() as conn:
            conn.execute(
                """INSERT INTO components VALUES(?,?,?,?,?,?,?,?,?,?,?,?)
                ON CONFLICT(component_id) DO UPDATE SET version=excluded.version,type=excluded.type,
                origin_json=excluded.origin_json,description=excluded.description,permissions_json=excluded.permissions_json,
                dependencies_json=excluded.dependencies_json,compatibility_json=excluded.compatibility_json,
                status=excluded.status,checksum=excluded.checksum,configuration_ref=excluded.configuration_ref,updated_at=excluded.updated_at""",
                (record["component_id"], record["version"], record["type"], canonical_json(record["origin"]),
                 record["description"], canonical_json(record["permissions"]), canonical_json(record["dependencies"]),
                 canonical_json(record["compatibility"]), record["status"], record["checksum"], record.get("configuration_ref"), utc_now()),
            )

    def get_component(self, component_id: str) -> dict[str, Any]:
        row = self.connection.execute("SELECT * FROM components WHERE component_id=?", (component_id,)).fetchone()
        if row is None:
            raise OrchestraError(ErrorCode.NOT_FOUND, f"component not found: {component_id}")
        result = dict(row)
        for field in ("origin_json", "permissions_json", "dependencies_json", "compatibility_json"):
            result[field.removesuffix("_json")] = json.loads(result.pop(field))
        return result

