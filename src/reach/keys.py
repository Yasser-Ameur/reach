"""Key combinations such as "ctrl+s" to Windows virtual key codes. Pure Python."""

from reach.guard import Refused

_CTRL, _SHIFT, _ALT, _TAB, _ESC, _INSERT = 0x11, 0x10, 0x12, 0x09, 0x1B, 0x2D

# No Windows key: every combination with it is handled by the shell, not the app.
_NAMED = {
    "ctrl": _CTRL,
    "shift": _SHIFT,
    "alt": _ALT,
    "enter": 0x0D,
    "tab": _TAB,
    "esc": _ESC,
    "escape": _ESC,
    "backspace": 0x08,
    "delete": 0x2E,
    "insert": _INSERT,
    "space": 0x20,
    "left": 0x25,
    "up": 0x26,
    "right": 0x27,
    "down": 0x28,
    "home": 0x24,
    "end": 0x23,
    "pageup": 0x21,
    "pagedown": 0x22,
} | {f"f{n}": 0x6F + n for n in range(1, 25)}

# Keys that need the extended flag, or Shift plus an arrow selects nothing.
EXTENDED = frozenset({0x2E, 0x2D, 0x25, 0x26, 0x27, 0x28, 0x24, 0x23, 0x21, 0x22})


def parse(combo: str) -> list[int]:
    """Virtual key codes in press order.

    Raises ValueError on an unknown key, and Refused on a combination that acts
    outside the window it is sent to: one the shell handles (task switching, Start,
    Task Manager), or a paste, which would carry in whatever another app copied.
    """
    codes = []
    for part in combo.lower().split("+"):
        key = part.strip()
        if key in ("win", "windows", "super", "meta"):
            raise Refused(f"{combo!r} uses the Windows key, which the shell handles, not the app.")
        if key in _NAMED:
            codes.append(_NAMED[key])
        elif len(key) == 1 and key.isascii() and key.isalnum():
            codes.append(ord(key.upper()))
        else:
            raise ValueError(f"unknown key {part!r} in {combo!r}")
    held = set(codes)
    if (_ALT in held and held & {_TAB, _ESC}) or (_CTRL in held and _ESC in held):
        raise Refused(f"{combo!r} is handled by the shell, not the app.")
    if (_CTRL in held and ord("V") in held) or (_SHIFT in held and _INSERT in held):
        raise Refused(f"{combo!r} pastes the clipboard, which may hold another app's data.")
    return codes
