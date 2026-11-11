"""Allowlist-oriented redaction for persisted payloads."""

from __future__ import annotations

from hashlib import sha256
import json
import re
from pathlib import PurePath
from typing import Any


SENSITIVE_KEY = re.compile(r"(prompt|response|reasoning|secret|token|password|credential|api[_-]?key|tool[_-]?args?)", re.IGNORECASE)
WINDOWS_ABSOLUTE = re.compile(r"^[A-Za-z]:[\\/]")


def canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def digest(value: Any) -> str:
    return sha256(canonical_json(value).encode("utf-8")).hexdigest()


def _looks_absolute(value: str) -> bool:
    return value.startswith(("/", "\\\\")) or bool(WINDOWS_ABSOLUTE.match(value))


def sanitize(value: Any, *, max_string: int = 2_000, max_items: int = 100) -> Any:
    if isinstance(value, dict):
        cleaned: dict[str, Any] = {}
        for index, (key, item) in enumerate(value.items()):
            if index >= max_items:
                cleaned["_truncated"] = True
                break
            key_text = str(key)
            if SENSITIVE_KEY.search(key_text):
                cleaned[key_text] = "[REDACTED]"
            else:
                cleaned[key_text] = sanitize(item, max_string=max_string, max_items=max_items)
        return cleaned
    if isinstance(value, (list, tuple, set)):
        result = [sanitize(item, max_string=max_string, max_items=max_items) for item in list(value)[:max_items]]
        if len(value) > max_items:
            result.append("[TRUNCATED]")
        return result
    if isinstance(value, str):
        if _looks_absolute(value):
            return f"[ABSOLUTE_PATH_REDACTED]/{PurePath(value.replace('\\\\', '/')).name}"
        return value if len(value) <= max_string else value[:max_string] + "[TRUNCATED]"
    if value is None or isinstance(value, (bool, int, float)):
        return value
    return str(value)[:max_string]

