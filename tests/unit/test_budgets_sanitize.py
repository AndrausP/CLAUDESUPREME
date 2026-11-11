from __future__ import annotations

import unittest

from orchestra_core.budgets import BudgetGuard, BudgetUsage, ReworkGuard, RetryPolicy
from orchestra_core.errors import ErrorCode, OrchestraError
from orchestra_core.models import BudgetProfile, Metric, MetricProvenance
from orchestra_core.sanitize import sanitize


class BudgetTests(unittest.TestCase):
    def test_enforces_operation_limit_even_when_tokens_unknown(self) -> None:
        usage = BudgetUsage(agent_runs=2, tokens=None)
        with self.assertRaises(OrchestraError) as raised:
            BudgetGuard(BudgetProfile.ECONOMY).validate(usage)
        self.assertEqual(ErrorCode.BUDGET_EXHAUSTED, raised.exception.code)

    def test_retry_backoff_is_bounded_and_deterministic_with_seed(self) -> None:
        first = RetryPolicy.next_delay(4, maximum=5, seed=7)
        second = RetryPolicy.next_delay(4, maximum=5, seed=7)
        self.assertEqual(first, second)
        self.assertLessEqual(first, 5)

    def test_repeated_defect_stops_rework(self) -> None:
        guard = ReworkGuard(3)
        guard.record("same bug")
        with self.assertRaises(OrchestraError) as raised:
            guard.record("Same Bug")
        self.assertEqual(ErrorCode.REWORK_LOOP, raised.exception.code)

    def test_unknown_metric_cannot_have_fabricated_value(self) -> None:
        with self.assertRaises(ValueError):
            Metric("tokens", 10, "token", MetricProvenance.UNKNOWN, "unavailable")


class SanitizationTests(unittest.TestCase):
    def test_redacts_sensitive_keys_and_absolute_paths(self) -> None:
        cleaned = sanitize({"prompt": "secret text", "api_key": "abc", "path": "C:\\private\\file.txt", "ok": 1})
        self.assertEqual("[REDACTED]", cleaned["prompt"])
        self.assertEqual("[REDACTED]", cleaned["api_key"])
        self.assertIn("ABSOLUTE_PATH_REDACTED", cleaned["path"])
        self.assertEqual(1, cleaned["ok"])


if __name__ == "__main__":
    unittest.main()

