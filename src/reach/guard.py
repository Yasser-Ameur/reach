"""The guard: the one check every tool call passes. Pure Python, no Windows calls."""

import json
import threading
import time
from collections.abc import Callable, Iterator
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path

SHELLS = frozenset(
    {
        "bash.exe",
        "cmd.exe",
        "conhost.exe",
        "explorer.exe",
        "mintty.exe",
        "openconsole.exe",
        "powershell.exe",
        "pwsh.exe",
        "python.exe",
        "windowsterminal.exe",
        "wsl.exe",
    }
)


class Refused(Exception):
    """A tool call the guard will not let through."""


@dataclass(frozen=True)
class App:
    path: str  # full executable path, lower case
    pid: int

    @property
    def name(self) -> str:
        return self.path.rsplit("\\", 1)[-1]


class Guard:
    def __init__(self, home: Path, ask: Callable[[App], bool], own_pid: int) -> None:
        self._grants_file = home / "grants.json"
        self._log_file = home / "actions.jsonl"
        self._ask = ask
        self._own_pid = own_pid
        self._denied: set[str] = set()
        self._turn = threading.Lock()
        self.killed = threading.Event()
        home.mkdir(parents=True, exist_ok=True)

    def _grants(self) -> list[str]:
        # Read every time, so deleting a line revokes without a restart.
        try:
            data = json.loads(self._grants_file.read_text(encoding="utf-8"))
        except FileNotFoundError:
            return []
        return [str(p).lower() for p in data]

    def granted(self, app: App | None) -> bool:
        return app is not None and app.path in self._grants()

    @contextmanager
    def turn(self) -> Iterator[None]:
        """One tool call at a time. A call arriving while another runs, or while
        the allow dialog is open, is refused and never queued behind it."""
        if self.killed.is_set():
            raise Refused("the kill switch was pressed. Restart the Reach server to continue.")
        if not self._turn.acquire(blocking=False):
            raise Refused("another Reach call or an allow dialog is still open.")
        try:
            yield
        finally:
            self._turn.release()

    def check(self, app: App | None) -> App:
        if self.killed.is_set():
            raise Refused("the kill switch was pressed. Restart the Reach server to continue.")
        if app is None:
            raise Refused("this window's process cannot be inspected; it may run elevated.")
        if app.pid == self._own_pid:
            raise Refused("Reach never acts on its own windows.")
        if app.path in self._grants():
            return app
        if app.path in self._denied:
            raise Refused(f"the owner declined {app.name} for this run.")
        if not self._ask(app):
            self._denied.add(app.path)
            raise Refused(f"the owner declined {app.name}.")
        if self.killed.is_set():  # pressed while the dialog was open: it outranks the yes
            raise Refused("the kill switch was pressed. Restart the Reach server to continue.")
        self._grants_file.write_text(
            json.dumps([*self._grants(), app.path], indent=2), encoding="utf-8"
        )
        return app

    def check_target(self, app: App, actual: App | None, where: str) -> None:
        """The input must land on the app that was named, not on whatever is there."""
        if actual is None or actual.path != app.path:
            owner = actual.name if actual else "a window Reach cannot inspect"
            raise Refused(f"{where} belongs to {owner}, not {app.name}.")

    def check_keys(self, focus_is_password: bool) -> None:
        if focus_is_password:
            raise Refused("keyboard focus is in a password field. The owner types passwords.")

    def log(self, tool: str, app: App | None, outcome: str, detail: dict[str, object]) -> None:
        entry = {
            "ts": time.strftime("%Y-%m-%dT%H:%M:%S"),
            "tool": tool,
            "app": app.path if app else None,
            "outcome": outcome,
            **detail,
        }
        with self._log_file.open("a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
