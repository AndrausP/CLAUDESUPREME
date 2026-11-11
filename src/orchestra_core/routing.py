"""Explainable deterministic task routing."""

from __future__ import annotations

from dataclasses import dataclass, field

from .models import CandidateDecision, RiskLevel, RoutingMode


@dataclass(frozen=True, slots=True)
class TaskSignals:
    mutation: bool = False
    areas: int = 1
    uncertainty: int = 0
    security: bool = False
    data_migration: bool = False
    destructive: bool = False
    reversible: bool = True
    external_dependencies: int = 0
    validations: int = 1


@dataclass(frozen=True, slots=True)
class AgentCapability:
    agent_id: str
    capabilities: frozenset[str]
    leader: bool = False


@dataclass(slots=True)
class RoutingDecision:
    mode: RoutingMode
    risk: RiskLevel
    selected_agents: list[CandidateDecision] = field(default_factory=list)
    rejected_candidates: list[CandidateDecision] = field(default_factory=list)


class Router:
    def classify(self, signals: TaskSignals) -> tuple[RoutingMode, RiskLevel]:
        high_risk = signals.security or signals.data_migration or signals.destructive
        if high_risk:
            return RoutingMode.DEEP, RiskLevel.CRITICAL if signals.destructive else RiskLevel.HIGH
        score = (
            int(signals.mutation)
            + max(0, signals.areas - 1)
            + signals.uncertainty
            + signals.external_dependencies
            + max(0, signals.validations - 1)
            + int(not signals.reversible)
        )
        if score == 0:
            return RoutingMode.DIRECT, RiskLevel.LOW
        if score <= 2 and signals.areas == 1:
            return RoutingMode.LEAN, RiskLevel.LOW
        if score <= 6:
            return RoutingMode.STANDARD, RiskLevel.MEDIUM
        return RoutingMode.DEEP, RiskLevel.HIGH

    def route(
        self,
        signals: TaskSignals,
        required_capabilities: set[str],
        candidates: list[AgentCapability],
    ) -> RoutingDecision:
        mode, risk = self.classify(signals)
        uncovered = set(required_capabilities)
        selected: list[CandidateDecision] = []
        remaining = list(candidates)
        while uncovered:
            scored = sorted(
                ((len(agent.capabilities & uncovered), agent.agent_id, agent) for agent in remaining),
                key=lambda item: (-item[0], item[1]),
            )
            if not scored or scored[0][0] == 0:
                break
            _, _, best = scored[0]
            selected.append(CandidateDecision(best.agent_id, "CAPABILITY_MATCH"))
            uncovered -= best.capabilities
            remaining.remove(best)

        # Leaders add value only when coordination or approval is actually required.
        needs_leader = len(selected) > 1 or risk in {RiskLevel.HIGH, RiskLevel.CRITICAL}
        leaders = [agent for agent in remaining if agent.leader]
        if needs_leader and leaders:
            leader = sorted(leaders, key=lambda item: item.agent_id)[0]
            selected.append(CandidateDecision(leader.agent_id, "COORDINATION_REQUIRED"))
            remaining.remove(leader)

        rejected: list[CandidateDecision] = []
        for agent in sorted(remaining, key=lambda item: item.agent_id):
            reason = "NO_COORDINATION_NEEDED" if agent.leader else "CAPABILITY_NOT_REQUIRED"
            rejected.append(CandidateDecision(agent.agent_id, reason))
        if uncovered:
            rejected.append(CandidateDecision("unresolved", "CAPABILITY_UNAVAILABLE:" + ",".join(sorted(uncovered))))
        return RoutingDecision(mode, risk, selected, rejected)

