"""Drive the real tools against scripts/target.py on this desktop.

Usage: python scripts/live_check.py [png-output-path]

The owner at the allow dialog is replaced by an automatic yes, and grants go to a
temporary folder, so nothing in ~/.reach is touched. Takes the mouse for a few seconds.
"""

import os
import subprocess
import sys
import tempfile
import time
from pathlib import Path

from mcp.server.mcpserver.exceptions import ToolError

from reach import server, win32
from reach.guard import Guard
from reach.overlay import Overlay

TEXT = "Reach was here: héllo ✓"
TEST_KEY = 0x7B  # F12: the check has its own kill switch, Ctrl+Alt+F12


def refused(call: object, *args: object) -> str:
    try:
        call(*args)  # type: ignore[operator]
    except ToolError as error:
        return str(error)
    raise AssertionError(f"{call} was not refused")


def ref_of(snapshot: str, needle: str) -> str:
    line = next(line for line in snapshot.splitlines() if needle in line)
    return line.split("[")[1].split("]")[0]


def main() -> None:
    home = Path(tempfile.mkdtemp(prefix="reach-live-"))
    server.guard = Guard(home, lambda app: True, os.getpid())
    win32.killed = server.guard.killed
    server.overlay = Overlay(server.guard.killed.set, key=TEST_KEY, shared="Local\\ReachLiveCheck")
    win32.init()
    server.overlay.start()

    target = subprocess.Popen([sys.executable, str(Path(__file__).with_name("target.py"))])
    try:
        deadline = time.monotonic() + 10
        window = 0
        while not window and time.monotonic() < deadline:
            time.sleep(0.2)
            window = next((h for h, title in win32.windows() if title == "Reach target"), 0)
        assert window, "target window never appeared"

        listing = server.windows()
        assert str(window) in listing, listing

        started = time.perf_counter()
        first = server.snapshot(window)
        print(f"snapshot: {len(first.splitlines())} lines in {time.perf_counter() - started:.2f}s")
        print(first)
        edits = [line for line in first.splitlines() if line.strip().startswith("Edit")]
        assert len(edits) == 2, "expected a text field and a password field"
        text_ref = edits[0].split("[")[1].split("]")[0]
        assert "value=[redacted]" in edits[1]

        server.click(window, ref=text_ref)
        server.type_text(window, TEXT)
        time.sleep(0.3)
        second = server.snapshot(window)
        assert TEXT in second, second
        print("typed text read back from the tree")

        # text_ref came from the first snapshot; a second one has been taken since.
        print("stale ref:", refused(server.click, window, text_ref))
        print("shell combo:", refused(server.press_key, window, "win+r"))

        server.click(window, ref=ref_of(second, "[redacted]"))
        time.sleep(0.2)
        print("password field:", refused(server.type_text, window, "hunter2"))
        assert "hunter2" not in server.snapshot(window)

        image = server.screenshot(window)
        if len(sys.argv) > 1:
            Path(sys.argv[1]).write_bytes(image.data or b"")
            print("screenshot written to", sys.argv[1])
        server.click(window, x=88, y=147)  # screenshot pixels, on the Press button
        time.sleep(0.2)
        pressed = next(s for s in server.snapshot(window).splitlines() if '"Press"' in s)
        assert "(focused)" in pressed, pressed
        print("click by screenshot pixels landed on the button")

        # A drag across the text field selects what is in it; typing then replaces it.
        server.drag(window, x=33, y=65, to_x=382, to_y=65)
        after_drag = server.type_text(window, "dragged", then_snapshot=True)
        assert 'value="dragged"' in after_drag, after_drag
        print("drag selected the text, and the action returned the new tree")

        # The same selection by click, then shift+click.
        server.click(window, x=33, y=65)
        server.click(window, x=382, y=65, modifiers="shift")
        after_shift = server.type_text(window, "shifted", then_snapshot=True)
        assert 'value="shifted"' in after_shift, after_shift
        print("shift+click extended the selection")

        found = server.snapshot(window, find="press")
        assert '"Press"' in found, found
        assert "Edit" not in found, found
        assert server.hover(window, ref=ref_of(found, '"Press"')) == "hovering"
        print("find kept only the match, and hover reached it")

        server.click(window, ref=ref_of(server.snapshot(window), "Edit"))
        win32.send_keys([0x11, 0x12, TEST_KEY])  # a real hotkey press, on the check's own key
        time.sleep(0.3)
        print("after kill switch:", refused(server.snapshot, window))
        print("log lines:", len((home / "actions.jsonl").read_text("utf-8").splitlines()))
        print("LIVE CHECK PASSED")
    finally:
        target.kill()


if __name__ == "__main__":
    main()
