"""The wiring: each tool runs its guard checks before anything reaches the desktop.

Windows is replaced by a fake desktop with two windows. Window 1 is Notepad, which
the owner allows; window 2 is a mail app, which the owner declines. Removing a guard
call from server.py must turn one of these red.
"""

import json
from pathlib import Path
from types import SimpleNamespace

import pytest
from mcp.server.mcpserver.exceptions import ToolError

from reach import server, win32
from reach.guard import App, Guard, Refused
from reach.tree import Node

NOTEPAD = App(path=r"c:\windows\notepad.exe", pid=10)
MAIL = App(path=r"c:\apps\mail.exe", pid=11)
SAVE_CENTRE = (20, 20)


@pytest.fixture
def desk(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> SimpleNamespace:
    state = SimpleNamespace(sent=[], under_point=1, foreground=1, password=False, home=tmp_path)
    guard = Guard(tmp_path, lambda app: app == NOTEPAD, own_pid=99)
    tree = Node(
        role="Window",
        name="Untitled",
        rect=(0, 0, 100, 100),
        children=[Node(role="Button", name="Save", rect=(10, 10, 30, 30))],
    )

    def record(kind: str) -> object:
        return lambda *args: state.sent.append((kind, *args))

    monkeypatch.setattr(server, "guard", guard)
    monkeypatch.setattr(server, "overlay", SimpleNamespace(show=lambda: None))
    monkeypatch.setattr(server, "_refs", {})
    monkeypatch.setattr(server, "_scales", {})
    monkeypatch.setattr(win32, "killed", guard.killed)
    monkeypatch.setattr(win32, "app_of", {1: NOTEPAD, 2: MAIL}.get)
    monkeypatch.setattr(win32, "rect_of", lambda hwnd: (0, 0, 100, 100))
    monkeypatch.setattr(win32, "focus", lambda hwnd: None)
    monkeypatch.setattr(win32, "root_at", lambda x, y: state.under_point)
    monkeypatch.setattr(win32, "foreground", lambda: state.foreground)
    monkeypatch.setattr(win32, "capture", lambda hwnd, side: (1, 1, bytes(4), 1.0))
    for kind in ("click", "scroll", "send_text", "send_keys"):
        monkeypatch.setattr(win32, kind, record(kind))
    monkeypatch.setattr(server.uia, "focus_is_password", lambda: state.password)
    monkeypatch.setattr(server.uia, "snapshot", lambda hwnd: tree)
    return state


def save_ref(window: int = 1) -> str:
    line = next(line for line in server.snapshot(window).splitlines() if '"Save"' in line)
    return line.split("[")[1].split("]")[0]


def log(desk: SimpleNamespace) -> list[dict[str, object]]:
    lines = (desk.home / "actions.jsonl").read_text(encoding="utf-8").splitlines()
    return [json.loads(line) for line in lines]


def test_tool_read_needs_grant(desk: SimpleNamespace) -> None:
    with pytest.raises(ToolError, match="Refused: the owner declined"):
        server.snapshot(2)
    with pytest.raises(ToolError, match="Refused"):
        server.screenshot(2)
    assert server.screenshot(1).data


def test_tool_click_checks_app_under_point(desk: SimpleNamespace) -> None:
    ref = save_ref()
    desk.under_point = 2  # the mail app sits over the button
    with pytest.raises(ToolError, match=r"the point belongs to mail\.exe"):
        server.click(1, ref=ref)
    with pytest.raises(ToolError, match="Refused"):
        server.scroll(1, -3, ref=ref)
    assert desk.sent == []
    desk.under_point = 1
    server.click(1, ref=ref)
    assert desk.sent == [("click", *SAVE_CENTRE, "left", False)]


def test_tool_keys_check_foreground(desk: SimpleNamespace) -> None:
    desk.foreground = 2  # focus could not be moved to Notepad
    with pytest.raises(ToolError, match="keyboard focus belongs to mail"):
        server.type_text(1, "hello")
    with pytest.raises(ToolError, match="Refused"):
        server.press_key(1, "enter")
    assert desk.sent == []


def test_tool_password_focus_refuses_keys_and_keeps_text_out_of_log(desk: SimpleNamespace) -> None:
    desk.password = True
    with pytest.raises(ToolError, match="password field"):
        server.type_text(1, "hunter2")
    with pytest.raises(ToolError, match="password field"):
        server.press_key(1, "a")
    assert desk.sent == []
    assert "hunter2" not in (desk.home / "actions.jsonl").read_text(encoding="utf-8")


def test_tool_old_ref_is_refused(desk: SimpleNamespace) -> None:
    old = save_ref()
    new = save_ref()
    assert old != new
    with pytest.raises(ToolError, match="not in the latest snapshot"):
        server.click(1, ref=old)
    assert desk.sent == []


@pytest.mark.parametrize(
    "combo", ["win+r", "win+e", "alt+tab", "alt+esc", "ctrl+esc", "ctrl+shift+esc", "ctrl+v"]
)
def test_tool_shell_and_paste_combos_refused(desk: SimpleNamespace, combo: str) -> None:
    with pytest.raises(ToolError, match="Refused"):
        server.press_key(1, combo)
    assert desk.sent == []


def test_tool_ordinary_combo_is_sent(desk: SimpleNamespace) -> None:
    server.press_key(1, "ctrl+s")
    assert desk.sent == [("send_keys", [0x11, ord("S")])]


def test_tool_every_call_logged(desk: SimpleNamespace) -> None:
    server.windows()
    server.type_text(1, "hello")
    with pytest.raises(ToolError):
        server.snapshot(2)
    entries = log(desk)
    assert [(e["tool"], e["app"], e["outcome"]) for e in entries] == [
        ("windows", None, "ok"),
        ("type_text", NOTEPAD.path, "ok"),
        ("snapshot", MAIL.path, "refused: the owner declined mail.exe."),
    ]
    assert entries[1]["text"] == "hello"


def test_tool_refused_after_kill(desk: SimpleNamespace) -> None:
    ref = save_ref()
    server.guard.killed.set()
    with pytest.raises(ToolError, match="kill switch"):
        server.click(1, ref=ref)
    assert desk.sent == []


def test_kill_stops_input_already_in_flight(monkeypatch: pytest.MonkeyPatch) -> None:
    # The real send path, with the flag set: it must raise before SendInput is reached.
    killed = win32.threading.Event()
    killed.set()
    monkeypatch.setattr(win32, "killed", killed)
    with pytest.raises(Refused, match="kill switch"):
        win32.send_text("this must never be typed")


def test_tool_half_a_point_is_an_error(desk: SimpleNamespace) -> None:
    with pytest.raises(ValueError, match="both x and y"):
        server.click(1, x=5)
    assert desk.sent == []
