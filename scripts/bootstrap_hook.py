"""SessionStart hook: report plugin and optional CLI availability without mutation."""

from __future__ import annotations

import json
import shutil
import sys


def main() -> int:
    try:
        json.load(sys.stdin)
    except (json.JSONDecodeError, OSError):
        pass
    available = shutil.which("orchestra") is not None
    status = "available" if available else "not installed; native skills remain usable"
    print(f"Orchestra Core plugin loaded. CLI: {status}. Use /orchestra:doctor-org for diagnostics.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
