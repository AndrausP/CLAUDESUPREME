import json
from pathlib import Path
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

from guard_hook import is_destructive  # noqa: E402


DESTRUCTIVE = [
    "rm -rf build",
    "rm -fr build",
    "rm -r -f build",
    "rm -Rf build",
    "rm --recursive --force build",
    "rm -r --force build",
    "/bin/rm -rf /tmp/x",
    "sudo rm -rf /",
    "find . -name x | xargs rm -rf",
    "echo ok && rm -rf build",
    "echo ok; rm -fr build",
    "bash -c \"rm -rf build\"",
    "Remove-Item x -Recurse -Force",
    "Remove-Item -Force -Recurse x",
    "remove-item x -r -fo",
    "rm x -Recurse -Force",
    "powershell -NoProfile -Command \"Remove-Item C:\\x -Recurse -Force\"",
    "del /s /q C:\\x",
    "erase /s C:\\x\\*",
    "rd /s /q C:\\x",
    "rmdir /s C:\\x",
    "cmd /c del /s /q C:\\x",
    "git reset --hard",
    "git reset --hard HEAD~3",
    "git -C repo reset --hard",
    "git clean -fdx",
    "git clean -xdf",
    "git clean --force",
    "format c:",
    "format.com d: /q",
]

SAFE = [
    "ls -la",
    "rm file.txt",
    "rm -r build",
    "rm -f file.txt",
    "echo format c: is bad",
    "echo rm -rf is dangerous",
    "git reset --soft HEAD~1",
    "git reset HEAD file.py",
    "git clean -n",
    "git status",
    "Remove-Item file.txt",
    "Remove-Item dir -Recurse",
    "del file.txt",
    "rd emptydir",
    "python -m unittest discover -s tests",
    "grep -rf patterns.txt src",
    "npm run format",
]


class GuardHookTests(unittest.TestCase):
    def test_Should_Deny_When_CommandIsDestructive(self) -> None:
        for command in DESTRUCTIVE:
            with self.subTest(command=command):
                self.assertTrue(is_destructive(command))

    def test_Should_Allow_When_CommandIsSafe(self) -> None:
        for command in SAFE:
            with self.subTest(command=command):
                self.assertFalse(is_destructive(command))

    def _run(self, payload: object) -> str:
        return subprocess.run(
            [sys.executable, str(ROOT / "scripts" / "guard_hook.py")],
            input=json.dumps(payload),
            capture_output=True,
            text=True,
            check=True,
        ).stdout

    def test_Should_EmitDenyDecision_When_HookReceivesDestructiveBash(self) -> None:
        output = json.loads(self._run({"tool_name": "Bash", "tool_input": {"command": "rm -fr build"}}))
        self.assertEqual(output["hookSpecificOutput"]["permissionDecision"], "deny")

    def test_Should_EmitNothing_When_HookReceivesSafeCommand(self) -> None:
        self.assertEqual(self._run({"tool_name": "PowerShell", "tool_input": {"command": "Get-ChildItem"}}), "")

    def test_Should_Deny_When_WritingProtectedFile(self) -> None:
        output = json.loads(self._run({"tool_name": "Edit", "tool_input": {"file_path": "C:\\repo\\docs\\decisions.md"}}))
        self.assertEqual(output["hookSpecificOutput"]["permissionDecision"], "deny")


if __name__ == "__main__":
    unittest.main()
