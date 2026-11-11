"""PreToolUse guardrail for clearly destructive commands and policy writes."""

from __future__ import annotations

import json
import re
import sys


# Commands are split into segments at shell separators; each pattern only matches a
# segment's leading command, so arguments such as `echo format c:` are not flagged.
SEPARATORS = re.compile(r"&&|\|\||[;|\n&]|\$\(|`|\(|\)|\{|\}")
QUOTED = re.compile(r"\"([^\"]*)\"|'([^']*)'")
PREFIX = re.compile(
    r"^(?:(?:sudo|doas|nohup|time|command|builtin|exec|xargs)(?:\s+-\S+)*\s+"
    r"|env(?:\s+-\S+)*(?:\s+\w+=\S*)*\s+"
    r"|\w+=\S*\s+"
    r"|cmd(?:\.exe)?\s+/[ck]\s+"
    r"|(?:powershell|pwsh)(?:\.exe)?(?:\s+-\S+)*\s+)",
    re.IGNORECASE,
)

POSIX_RM = re.compile(r"^(?:\S*/)?rm(?:\.exe)?$", re.IGNORECASE)
PS_REMOVE = re.compile(r"^(?:remove-item|ri|rm|del|erase|rmdir|rd)$", re.IGNORECASE)
CMD_REMOVE = re.compile(r"^(?:del|erase|rmdir|rd)(?:\.exe)?$", re.IGNORECASE)
FORMAT = re.compile(r"^format(?:\.com)?\s+[a-z]:", re.IGNORECASE)
GIT_RESET_HARD = re.compile(r"^git(?:\s+-\S+(?:\s+\S+)?)*\s+reset\b.*\s--hard\b", re.IGNORECASE)
GIT_CLEAN = re.compile(r"^git(?:\s+-\S+(?:\s+\S+)?)*\s+clean\b", re.IGNORECASE)

PROTECTED = {
    "agents.md",
    ".claude-plugin/plugin.json",
    ".codex/state.json",
    "docs/decisions.md",
}


def _segments(command: str) -> list[str]:
    sources = [command] + [a or b for a, b in QUOTED.findall(command)]
    result: list[str] = []
    for source in sources:
        for part in SEPARATORS.split(source):
            segment = part.strip()
            while True:
                stripped = PREFIX.sub("", segment, count=1).strip()
                if stripped == segment:
                    break
                segment = stripped
            if segment:
                result.append(segment.strip("\"'"))
    return result


def _is_destructive(segment: str) -> bool:
    tokens = segment.split()
    head, args = tokens[0], tokens[1:]
    lowered = [arg.lower() for arg in args]
    if POSIX_RM.match(head):
        short = [arg[1:] for arg in args if arg.startswith("-") and not arg.startswith("--")]
        recursive = any("r" in flags.lower() for flags in short) or "--recursive" in lowered
        force = any("f" in flags for flags in short) or "--force" in lowered
        if recursive and force:
            return True
    if PS_REMOVE.match(head):
        recurse = any(re.fullmatch(r"-r(?:e(?:c(?:u(?:r(?:s(?:e)?)?)?)?)?)?", arg) for arg in lowered)
        force = any(re.fullmatch(r"-fo(?:r(?:c(?:e)?)?)?", arg) for arg in lowered)
        if recurse and force:
            return True
    if CMD_REMOVE.match(head) and "/s" in lowered:
        return True
    if FORMAT.match(segment) or GIT_RESET_HARD.match(segment):
        return True
    if GIT_CLEAN.match(segment):
        clean_args = segment.split("clean", 1)[1].split()
        if any(arg == "--force" or (arg.startswith("-") and not arg.startswith("--") and "f" in arg) for arg in clean_args):
            return True
    return False


def is_destructive(command: str) -> bool:
    return any(_is_destructive(segment) for segment in _segments(command))


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
    if tool in {"Bash", "PowerShell"} and is_destructive(command):
        return deny("Destructive command blocked. Use a user-mediated, target-specific recovery procedure.")
    if tool in {"Write", "Edit"}:
        path = str(payload.get("file_path") or payload.get("path") or "").replace("\\", "/").lower()
        if path.endswith("docs/knowledge/business-rules.md") or any(path.endswith(item) for item in PROTECTED):
            return deny("Policy or shared-memory file is protected; use the authorized governance workflow.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
