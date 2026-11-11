"""PreToolUse guardrail for clearly destructive commands and policy writes."""

from __future__ import annotations

import json
import re
import sys


DESTRUCTIVE = [
    re.compile(r"\brm\s+-[^\n]*r[^\n]*f\b", re.IGNORECASE),
    re.compile(r"\bremove-item\b[^\n]*(?:-recurse[^\n]*-force|-force[^\n]*-recurse)", re.IGNORECASE),
    re.compile(r"\bgit\s+reset\s+--hard\b", re.IGNORECASE),
    re.compile(r"\bgit\s+clean\s+-[^\n]*f", re.IGNORECASE),
    re.compile(r"\bformat(?:\.com)?\s+[a-z]:", re.IGNORECASE),
]
PROTECTED = {
    "agents.md",
    ".claude-plugin/plugin.json",
    ".codex/state.json",
    "docs/decisions.md",
}


def deny(reason: str) -> int:
    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "deny",
            "permissionDecisionReason": reason,
        }
    }))
    return 0


def main() -> int:
    try:
        data = json.load(sys.stdin)
    except (json.JSONDecodeError, OSError):
        return deny("Orchestra could not validate this tool request safely.")
    tool = str(data.get("tool_name", ""))
    payload = data.get("tool_input") or {}
    command = str(payload.get("command", ""))
    if tool in {"Bash", "PowerShell"} and any(pattern.search(command) for pattern in DESTRUCTIVE):
        return deny("Destructive command blocked. Use a user-mediated, target-specific recovery procedure.")
    if tool in {"Write", "Edit"}:
        path = str(payload.get("file_path") or payload.get("path") or "").replace("\\", "/").lower()
        if path.endswith("docs/knowledge/business-rules.md") or any(path.endswith(item) for item in PROTECTED):
            return deny("Policy or shared-memory file is protected; use the authorized governance workflow.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
