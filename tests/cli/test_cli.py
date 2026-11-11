from __future__ import annotations

from contextlib import redirect_stderr, redirect_stdout
import io
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from orchestra_core import cli
from orchestra_core.tui import tui_supported


class CliTest(unittest.TestCase):
    def invoke(self, *argv: str) -> tuple[int, str, str]:
        stdout, stderr = io.StringIO(), io.StringIO()
        with redirect_stdout(stdout), redirect_stderr(stderr):
            code = cli.main(list(argv))
        return code, stdout.getvalue(), stderr.getvalue()

    def test_parser_exposes_required_surface(self) -> None:
        help_text = cli.build_parser().format_help()
        for name in ("status", "bootstrap", "task", "route", "clareza", "agents", "departments", "skills", "memory", "budget", "pipeline", "doctor", "audit", "report", "extension", "ledger"):
            self.assertIn(name, help_text)

    def test_bootstrap_and_status_json_are_valid(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "pyproject.toml").write_text("[project]\nname='sample'\n", encoding="utf-8")
            code, output, error = self.invoke("bootstrap", "--project", directory, "--json")
            self.assertEqual(0, code, error)
            self.assertEqual("ready", json.loads(output)["state"])
            code, output, error = self.invoke("status", "--project", directory, "--json")
            self.assertEqual(0, code, error)
            self.assertEqual(0, json.loads(output)["active_tasks"])

    def test_task_lifecycle_uses_core(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "pyproject.toml").write_text("[project]\nname='sample'\n", encoding="utf-8")
            code, output, error = self.invoke("task", "create", "Example", "--objective", "Verify CLI", "--criteria", "It works", "--project", directory, "--json")
            self.assertEqual(0, code, error)
            task = json.loads(output)
            self.assertEqual("CREATED", task["status"])
            code, output, error = self.invoke("task", "show", task["task_id"], "--project", directory, "--json")
            self.assertEqual(0, code, error)
            self.assertEqual(task["task_id"], json.loads(output)["task_id"])

    def test_running_task_cancellation_persists_and_exposes_checkpoint(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "pyproject.toml").write_text("[project]\nname='sample'\n", encoding="utf-8")
            code, output, error = self.invoke(
                "task", "create", "Cancellable", "--objective", "Stop safely",
                "--project", directory, "--json",
            )
            self.assertEqual(0, code, error)
            task_id = json.loads(output)["task_id"]
            for target in ("CLASSIFIED", "PLANNED", "READY", "RUNNING"):
                code, output, error = self.invoke(
                    "task", "transition", task_id, target,
                    "--project", directory, "--json",
                )
                self.assertEqual(0, code, error)

            code, output, error = self.invoke(
                "task", "cancel", task_id,
                "--reason", "operator requested stop",
                "--evidence", "log:interrupt-request",
                "--project", directory, "--json",
            )

            self.assertEqual(0, code, error)
            cancelled = json.loads(output)
            self.assertEqual("CANCELLED", cancelled["status"])
            evidence = cancelled["cancellation_evidence"]
            self.assertEqual("pre-cancellation", evidence["step"])
            self.assertEqual("RUNNING", evidence["state"])
            self.assertEqual(["log:interrupt-request"], evidence["payload"]["evidence_refs"])
            self.assertTrue(evidence["payload"]["safe_to_resume"])

            code, output, error = self.invoke(
                "task", "show", task_id, "--project", directory, "--json",
            )
            self.assertEqual(0, code, error)
            persisted = json.loads(output)["checkpoint"]
            self.assertEqual(evidence["checkpoint_id"], persisted["checkpoint_id"])
            self.assertEqual("RUNNING", persisted["state"])

    def test_route_is_explainable_json(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "pyproject.toml").write_text("[project]\nname='sample'\n", encoding="utf-8")
            code, output, error = self.invoke("route", "--security", "--capability", "routing", "--project", directory, "--json")
            self.assertEqual(0, code, error)
            result = json.loads(output)
            self.assertEqual("DEEP", result["mode"])
            self.assertIn("selected_agents", result)
            self.assertIn("rejected_candidates", result)

    def test_term_dumb_forces_plain_without_ansi(self) -> None:
        parser = cli.build_parser()
        args = parser.parse_args(["status"])
        with patch.dict(os.environ, {"TERM": "dumb"}, clear=False):
            self.assertEqual("plain", cli.renderer_name(args))
        code, output, error = self.invoke("doctor", "--plain")
        self.assertEqual(0, code, error)
        self.assertNotIn("\x1b[", output)

    def test_ascii_fallback_is_cp850_safe(self) -> None:
        value = cli._ascii_safe("execução — concluída", "ascii")
        value.encode("ascii")
        self.assertNotIn("—", value)

    def test_json_never_uses_ansi(self) -> None:
        code, output, error = self.invoke("budget", "list", "--json")
        self.assertEqual(0, code, error)
        json.loads(output)
        self.assertNotIn("\x1b[", output)

    def test_tui_falls_back_when_dependency_missing_or_term_dumb(self) -> None:
        with patch.dict(os.environ, {"TERM": "dumb"}, clear=False):
            supported, reason = tui_supported()
        self.assertFalse(supported)
        self.assertEqual("term-dumb" if __import__("importlib").util.find_spec("textual") else "textual-not-installed", reason)

    def test_narrow_terminal_forces_plain(self) -> None:
        parser = cli.build_parser()
        args = parser.parse_args(["status"])
        with patch("orchestra_core.cli._terminal_size", return_value=os.terminal_size((60, 20))):
            self.assertTrue(cli.plain_required(args))


if __name__ == "__main__":
    unittest.main()
