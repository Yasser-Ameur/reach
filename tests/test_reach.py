"""The pure half of Reach. Test names match the ids cited in docs/THREAT-MODEL.md."""

import json
import struct
import zlib
from pathlib import Path

import pytest

from reach import keys, png
from reach.guard import App, Guard, Refused
from reach.tree import Node, render

NOTEPAD = App(path=r"c:\windows\notepad.exe", pid=10)
MAIL = App(path=r"c:\apps\mail.exe", pid=11)
OWN_PID = 99


class Owner:
    """Stands in for the person at the allow dialog."""

    def __init__(self, answer: bool) -> None:
        self.answer = answer
        self.asked: list[App] = []

    def __call__(self, app: App) -> bool:
        self.asked.append(app)
        return self.answer


def make(tmp_path: Path, answer: bool) -> tuple[Guard, Owner]:
    owner = Owner(answer)
    return Guard(tmp_path, owner, OWN_PID), owner


def test_read_needs_grant(tmp_path: Path) -> None:
    guard, owner = make(tmp_path, answer=False)
    with pytest.raises(Refused):
        guard.check(NOTEPAD)
    assert owner.asked == [NOTEPAD]
    assert not guard.granted(NOTEPAD)


def test_yes_is_persisted_and_not_asked_again(tmp_path: Path) -> None:
    guard, owner = make(tmp_path, answer=True)
    guard.check(NOTEPAD)
    guard.check(NOTEPAD)
    assert owner.asked == [NOTEPAD]
    second_run, second_owner = make(tmp_path, answer=False)
    second_run.check(NOTEPAD)
    assert second_owner.asked == []


def test_grant_keyed_by_path(tmp_path: Path) -> None:
    guard, _ = make(tmp_path, answer=True)
    guard.check(NOTEPAD)
    guard._ask = Owner(False)
    impostor = App(path=r"c:\users\me\downloads\notepad.exe", pid=12)
    with pytest.raises(Refused):
        guard.check(impostor)


def test_denial_cached(tmp_path: Path) -> None:
    guard, owner = make(tmp_path, answer=False)
    for _ in range(3):
        with pytest.raises(Refused):
            guard.check(MAIL)
    assert len(owner.asked) == 1


def test_revoking_a_line_takes_effect_without_restart(tmp_path: Path) -> None:
    guard, owner = make(tmp_path, answer=True)
    guard.check(NOTEPAD)
    (tmp_path / "grants.json").write_text("[]", encoding="utf-8")
    owner.answer = False
    with pytest.raises(Refused):
        guard.check(NOTEPAD)


def test_own_process_refused(tmp_path: Path) -> None:
    guard, owner = make(tmp_path, answer=True)
    with pytest.raises(Refused, match="own windows"):
        guard.check(App(path=r"c:\python\python.exe", pid=OWN_PID))
    assert owner.asked == []


def test_uninspectable_refused(tmp_path: Path) -> None:
    guard, owner = make(tmp_path, answer=True)
    with pytest.raises(Refused, match="elevated"):
        guard.check(None)
    assert owner.asked == []


def test_pending_dialog_blocks_input(tmp_path: Path) -> None:
    seen: list[str] = []

    def owner_still_reading(app: App) -> bool:
        # A second tool call arrives while the dialog is on screen.
        with pytest.raises(Refused, match="allow dialog"), guard.turn():
            seen.append("input was sent")
        return True

    guard = Guard(tmp_path, owner_still_reading, OWN_PID)
    with guard.turn():
        guard.check(NOTEPAD)
    assert seen == []
    with guard.turn():  # and the turn is free again afterwards
        pass


def test_click_checks_app_under_point(tmp_path: Path) -> None:
    guard, _ = make(tmp_path, answer=True)
    guard.check_target(NOTEPAD, App(path=NOTEPAD.path, pid=77), "the point")
    with pytest.raises(Refused, match=r"mail\.exe, not notepad\.exe"):
        guard.check_target(NOTEPAD, MAIL, "the point")


def test_keys_check_foreground(tmp_path: Path) -> None:
    guard, _ = make(tmp_path, answer=True)
    with pytest.raises(Refused, match="cannot inspect"):
        guard.check_target(NOTEPAD, None, "keyboard focus")


def test_password_focus_refuses_keys(tmp_path: Path) -> None:
    guard, _ = make(tmp_path, answer=True)
    guard.check_keys(focus_is_password=False)
    with pytest.raises(Refused, match="password"):
        guard.check_keys(focus_is_password=True)


def test_killed_refuses_everything(tmp_path: Path) -> None:
    guard, owner = make(tmp_path, answer=True)
    guard.check(NOTEPAD)
    guard.killed.set()
    with pytest.raises(Refused, match="kill switch"):
        guard.check(NOTEPAD)
    with pytest.raises(Refused, match="kill switch"), guard.turn():
        pass
    assert owner.asked == [NOTEPAD]


def test_every_call_logged(tmp_path: Path) -> None:
    guard, _ = make(tmp_path, answer=True)
    guard.log("type_text", NOTEPAD, "ok", {"text": "héllo"})
    guard.log("click", None, "refused: no", {"ref": "e1"})
    lines = (tmp_path / "actions.jsonl").read_text(encoding="utf-8").splitlines()
    first, second = (json.loads(line) for line in lines)
    assert (first["tool"], first["app"], first["outcome"], first["text"]) == (
        "type_text",
        NOTEPAD.path,
        "ok",
        "héllo",
    )
    assert (second["app"], second["outcome"]) == (None, "refused: no")


def test_render_gives_refs_and_states() -> None:
    root = Node(
        role="Window",
        name="Untitled",
        children=[
            Node(role="Button", name="Save", rect=(10, 20, 30, 40), enabled=False),
            Node(role="Edit", name="Body", value="line one\nline two", focused=True),
            Node(role="Pane"),  # nameless and empty: noise, dropped
            Node(role="Button", name="Hidden", offscreen=True),
            Node(role="Edit"),  # nameless and empty, but somewhere to type: kept
        ],
    )
    text, refs = render(root, 1)
    assert text.splitlines() == [
        'Window "Untitled" [s1e1]',
        '  Button "Save" [s1e2] (disabled)',
        '  Edit "Body" [s1e3] value="line one line two" (focused)',
        "  Edit [s1e4]",
    ]
    assert refs["s1e2"] == (10, 20, 30, 40)
    assert "Hidden" not in text


def test_password_value_redacted() -> None:
    text, _ = render(Node(role="Edit", name="Password", value="hunter2", password=True), 1)
    assert "hunter2" not in text
    assert "value=[redacted]" in text


def test_render_truncates_at_the_limit() -> None:
    root = Node(role="List", name="l", children=[Node(role="Text", name=str(i)) for i in range(50)])
    text, refs = render(root, 1, limit=10)
    assert len(refs) == 10
    assert text.splitlines()[-1] == "... truncated at 10 elements"


def test_keys_parse() -> None:
    assert keys.parse("Ctrl+Shift+S") == [0x11, 0x10, ord("S")]
    assert keys.parse("f5") == [0x74]
    assert keys.parse("alt + f4") == [0x12, 0x73]
    with pytest.raises(ValueError, match="unknown key"):
        keys.parse("ctrl+banana")


@pytest.mark.parametrize("combo", ["win+r", "alt+tab", "ctrl+esc", "ctrl+v", "shift+insert"])
def test_keys_refuse_shell_and_paste_combos(combo: str) -> None:
    with pytest.raises(Refused):
        keys.parse(combo)


def test_png_round_trips_pixels() -> None:
    blue_then_red = bytes([255, 0, 0, 255, 0, 0, 255, 255])  # two BGRA pixels
    data = png.encode(2, 1, blue_then_red)
    assert data[:8] == b"\x89PNG\r\n\x1a\n"
    assert struct.unpack(">II", data[16:24]) == (2, 1)
    idat = data[data.index(b"IDAT") + 4 : data.index(b"IEND") - 8]
    assert zlib.decompress(idat) == b"\x00" + bytes([0, 0, 255, 255, 0, 0])
