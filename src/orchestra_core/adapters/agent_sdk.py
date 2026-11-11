"""Port-compatible optional Claude Agent SDK adapter."""

from __future__ import annotations

from dataclasses import dataclass
from importlib.util import find_spec
from typing import Any

from ..errors import ErrorCode, OrchestraError


@dataclass(frozen=True, slots=True)
class AgentSDKAvailability:
    available: bool
    reason: str


class AgentSDKAdapter:
    """Detection-only baseline; execution requires explicit host configuration."""

    def availability(self) -> AgentSDKAvailability:
        installed = find_spec("claude_agent_sdk") is not None
        return AgentSDKAvailability(installed, "installed" if installed else "optional package claude_agent_sdk is not installed")

    def execute(self, *_: Any, authenticated: bool = False, **__: Any) -> None:
        status = self.availability()
        if not status.available:
            raise OrchestraError(ErrorCode.INCOMPATIBLE_VERSION, status.reason)
        if not authenticated:
            raise OrchestraError(ErrorCode.PERMISSION_DENIED, "Agent SDK execution requires host-managed official authentication")
        raise OrchestraError(ErrorCode.VALIDATION_INCONCLUSIVE, "programmatic execution is not enabled by the local-first baseline")

