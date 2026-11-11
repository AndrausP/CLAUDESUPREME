from __future__ import annotations

import unittest

from orchestra_core.errors import ErrorCode, OrchestraError
from orchestra_core.models import TaskStatus
from orchestra_core.routing import AgentCapability, Router, TaskSignals
from orchestra_core.workflow import StateMachine, TransitionRequest, VALID_TRANSITIONS


class WorkflowTests(unittest.TestCase):
    def request(self, source: TaskStatus, target: TaskStatus, evidence: tuple[str, ...] = ()) -> TransitionRequest:
        return TransitionRequest("task", 0, source, target, "agent", "tester", "TEST", "test", evidence)

    def test_exactly_thirteen_states_have_transition_entries(self) -> None:
        self.assertEqual(13, len(TaskStatus))
        self.assertEqual(set(TaskStatus), set(VALID_TRANSITIONS))

    def test_invalid_transition_is_typed(self) -> None:
        with self.assertRaises(OrchestraError) as raised:
            StateMachine.validate(self.request(TaskStatus.RUNNING, TaskStatus.COMPLETED), [])
        self.assertEqual(ErrorCode.INVALID_TRANSITION, raised.exception.code)

    def test_completed_requires_passed_criteria_and_evidence(self) -> None:
        criteria = [{"id": "AC-1", "status": "passed"}]
        with self.assertRaises(OrchestraError) as raised:
            StateMachine.validate(self.request(TaskStatus.APPROVED, TaskStatus.COMPLETED), criteria)
        self.assertEqual(ErrorCode.VALIDATION_INCONCLUSIVE, raised.exception.code)
        StateMachine.validate(self.request(TaskStatus.APPROVED, TaskStatus.COMPLETED, ("evidence:1",)), criteria)


class RoutingTests(unittest.TestCase):
    def setUp(self) -> None:
        self.router = Router()

    def test_classifies_all_four_modes(self) -> None:
        self.assertEqual("DIRECT", self.router.classify(TaskSignals())[0].value)
        self.assertEqual("LEAN", self.router.classify(TaskSignals(mutation=True))[0].value)
        self.assertEqual("STANDARD", self.router.classify(TaskSignals(mutation=True, areas=2, uncertainty=1))[0].value)
        self.assertEqual("DEEP", self.router.classify(TaskSignals(security=True))[0].value)

    def test_selects_smallest_cover_and_skips_leader_when_unneeded(self) -> None:
        candidates = [
            AgentCapability("feature", frozenset({"backend", "tests"})),
            AgentCapability("test-only", frozenset({"tests"})),
            AgentCapability("lead", frozenset(), True),
        ]
        decision = self.router.route(TaskSignals(mutation=True), {"backend", "tests"}, candidates)
        self.assertEqual(["feature"], [item.id for item in decision.selected_agents])
        rejected = {item.id: item.reason_code for item in decision.rejected_candidates}
        self.assertEqual("NO_COORDINATION_NEEDED", rejected["lead"])

    def test_security_elevates_and_adds_leader(self) -> None:
        candidates = [
            AgentCapability("security", frozenset({"security"})),
            AgentCapability("architect", frozenset(), True),
        ]
        decision = self.router.route(TaskSignals(security=True), {"security"}, candidates)
        self.assertEqual("DEEP", decision.mode.value)
        self.assertEqual(["security", "architect"], [item.id for item in decision.selected_agents])


if __name__ == "__main__":
    unittest.main()

