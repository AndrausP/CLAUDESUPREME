"""Opt-in PostToolUse telemetry that stores metadata only, never tool arguments."""

from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import sys
import uuid


def main() -> int:
    if os.environ.get("ORCHESTRA_HOOK_TELEMETRY") != "1":
        return 0
    try:
        data = json.load(sys.stdin)
    except (json.JSONDecodeError, OSError):
        return 0
    project = Path(os.environ.get("CLAUDE_PROJECT_DIR") or Path.cwd())
    target = Path(os.environ.get("ORCHESTRA_HOOK_EVENT_FILE") or project / ".orchestra" / "events" / "plugin-hooks.jsonl")
    target.parent.mkdir(parents=True, exist_ok=True)
    session = str(data.get("session_id", "unknown"))
    record = {
        "schema_version": "1.0.0",
        "event_id": str(uuid.uuid4()),
        "event_type": "tool.completed",
        "occurred_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "tool": str(data.get("tool_name", "unknown")),
        "session_hash": hashlib.sha256(session.encode("utf-8")).hexdigest()[:16],
        "provenance": "observed",
    }
    with target.open("a", encoding="utf-8", newline="\n") as stream:
        stream.write(json.dumps(record, ensure_ascii=False, separators=(",", ":")) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
