"""Optional Textual interface.

Textual is never imported at module import time. This keeps the CLI functional
on legacy Windows terminals and in minimal installations.
"""

from __future__ import annotations

import importlib.util
import os
from pathlib import Path
import shutil
import sys
from typing import Any


def tui_supported(force: bool = False) -> tuple[bool, str]:
    size = shutil.get_terminal_size(fallback=(80, 24))
    if importlib.util.find_spec("textual") is None:
        return False, "textual-not-installed"
    if force:
        return True, "forced"
    if os.environ.get("ORCHESTRA_ACCESSIBLE") == "1":
        return False, "accessible-plain-requested"
    if os.environ.get("TERM", "").lower() == "dumb":
        return False, "term-dumb"
    if not getattr(sys.stdout, "isatty", lambda: False)():
        return False, "stdout-not-tty"
    if size.columns < 80 or size.lines < 24:
        return False, "terminal-too-small"
    return True, "supported"


def launch_tui(root: Path, *, force: bool = False) -> bool:
    supported, _ = tui_supported(force)
    if not supported:
        return False

    # Imports stay inside the guarded branch so Textual remains optional.
    from textual.app import App, ComposeResult
    from textual.binding import Binding
    from textual.containers import VerticalScroll
    from textual.widgets import Footer, Header, Static, TabbedContent, TabPane

    class OrchestraApp(App[None]):
        CSS = """
        Screen { background: #0C0C0C; color: #F2F2F2; }
        Header { background: #161616; color: #BAF3DB; }
        Footer { background: #161616; color: #F2F2F2; }
        TabbedContent { height: 1fr; }
        TabPane { padding: 1 2; }
        .state { border: solid #6B6B6B; padding: 1 2; }
        """
        TITLE = "ORCHESTRA CORE"
        SUB_TITLE = root.name
        BINDINGS = [
            Binding("1", "tab('home')", "Home"),
            Binding("2", "tab('pipeline')", "Pipeline"),
            Binding("3", "tab('departments')", "Departments"),
            Binding("4", "tab('agents')", "Agents"),
            Binding("5", "tab('memory')", "Memory"),
            Binding("6", "tab('components')", "Skills/MCP"),
            Binding("7", "tab('execution')", "Execution"),
            Binding("q", "quit", "Quit"),
        ]

        def compose(self) -> ComposeResult:
            yield Header(show_clock=True)
            with TabbedContent(initial="home", id="sections"):
                for pane_id, title, text in (
                    ("home", "1 Home", "Organization ready. Use the CLI for mutations and evidence-backed actions."),
                    ("pipeline", "2 Pipeline", "Select a task with: orchestra pipeline TASK_ID"),
                    ("departments", "3 Departments", "Seven departments are available on demand. Viewing does not invoke agents."),
                    ("agents", "4 Agents", "Use: orchestra agents --department ID"),
                    ("memory", "5 Memory", "Use: orchestra memory search QUERY"),
                    ("components", "6 Skills/MCP", "Use: orchestra skills or orchestra extension list"),
                    ("execution", "7 Execution", "Use: orchestra audit --task-id TASK_ID"),
                ):
                    with TabPane(title, id=pane_id):
                        with VerticalScroll():
                            yield Static(text, classes="state")
            yield Footer()

        def action_tab(self, pane_id: str) -> None:
            tabs = self.query_one("#sections", TabbedContent)
            tabs.active = pane_id

    try:
        OrchestraApp().run()
    except Exception:
        return False
    return True


__all__ = ["launch_tui", "tui_supported"]
