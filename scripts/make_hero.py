"""Produce docs/assets/hero.svg, the animated picture at the top of the README.

    python scripts/make_hero.py            capture, then build
    python scripts/make_hero.py --reuse    build again from the last capture

Capture drives the real tools against Windows Calculator: one snapshot, four clicks
by ref (7 + 5 =), one more snapshot to read the result. It also raises the real allow
dialog, photographs it and answers No. Every picture and every line of text in the
hero comes from that run, saved under docs/assets/capture/. Nothing is drawn by hand
except the frame around them. Capture takes the mouse for a few seconds.

Names in the capture are in the language Windows is set to; buttons are found by
their place in the tree, so the script runs on any language.
"""

import base64
import json
import os
import subprocess
import sys
import tempfile
import threading
import time
from html import escape
from pathlib import Path

ASSETS = Path(__file__).resolve().parent.parent / "docs" / "assets"
CAPTURE = ASSETS / "capture"
FRAME_SIDE = 760
TEST_KEY = 0x7B  # F12: the capture has its own kill switch, Ctrl+Alt+F12


def capture() -> None:
    from reach import png, server, win32
    from reach.guard import Guard
    from reach.overlay import Overlay

    user32 = win32.user32
    server.guard = Guard(
        Path(tempfile.mkdtemp(prefix="reach-hero-")), lambda app: True, os.getpid()
    )
    win32.killed = server.guard.killed
    server.overlay = Overlay(server.guard.killed.set, key=TEST_KEY, shared="Local\\ReachLiveCheck")
    win32.init()
    server.overlay.start()
    CAPTURE.mkdir(parents=True, exist_ok=True)

    def shoot(hwnd: int, name: str) -> list[int]:
        width, height, pixels, _ = win32.capture(hwnd, FRAME_SIDE)
        (CAPTURE / name).write_bytes(png.encode(width, height, pixels))
        return [width, height]

    def new_window(before: set[int], title: str | None = None) -> int:
        for _ in range(60):
            time.sleep(0.2)
            for hwnd, text in win32.windows():
                if hwnd not in before and (title is None or text == title):
                    return hwnd
        raise RuntimeError("the window never appeared")

    before = {hwnd for hwnd, _ in win32.windows()}
    subprocess.Popen(["calc.exe"])
    window = new_window(before)
    time.sleep(1.5)
    app = win32.app_of(window)
    assert app is not None

    # The real allow dialog for this app, photographed and answered No.
    before = {hwnd for hwnd, _ in win32.windows()}
    threading.Thread(target=server._ask, args=(app,), daemon=True).start()
    dialog = new_window(before, "Reach")
    time.sleep(0.6)
    dialog_size = shoot(dialog, "dialog.png")
    user32.PostMessageW(dialog, 0x0111, 7, 0)  # WM_COMMAND, IDNO
    time.sleep(0.5)

    server.press_key(window, "escape")
    started = time.perf_counter()
    first = server.snapshot(window)
    seconds = time.perf_counter() - started
    lines = first.splitlines()

    def buttons_of_group(count: int) -> list[str]:
        """The Button lines of the one Group that has exactly `count` of them."""
        for index, line in enumerate(lines):
            if line.strip().startswith("Group"):
                depth = len(line) - len(line.lstrip())
                inside = []
                for later in lines[index + 1 :]:
                    if len(later) - len(later.lstrip()) <= depth:
                        break
                    inside.append(later)
                if len(inside) == count and all(b.strip().startswith("Button") for b in inside):
                    return inside
        raise RuntimeError(f"no group of {count} buttons")

    digits, operators = buttons_of_group(11), buttons_of_group(5)
    left, top, right, bottom = win32.rect_of(window)
    steps = []
    frames = [shoot(window, "frame0.png")]
    for number, line in enumerate([digits[7], operators[3], digits[5], operators[4]], start=1):
        ref = line.split("[")[1].split("]")[0]
        rect = server._refs[window][ref]
        server.click(window, ref=ref)
        time.sleep(0.5)
        frames.append(shoot(window, f"frame{number}.png"))
        steps.append(
            {
                "ref": ref,
                "line": line.strip(),
                "x": ((rect[0] + rect[2]) / 2 - left) / (right - left),
                "y": ((rect[1] + rect[3]) / 2 - top) / (bottom - top),
            }
        )
    last = server.snapshot(window).splitlines()
    display = next(
        line.strip() for line in last if line.strip().startswith("Text") and "12" in line
    )
    server.press_key(window, "alt+f4")

    (CAPTURE / "capture.json").write_text(
        json.dumps(
            {
                "app": app.name,
                "window": window,
                "elements": len(lines) - 1,
                "seconds": round(seconds, 2),
                "header": lines[0],
                "steps": steps,
                "display": display,
                "frame": frames[0],
                "dialog": dialog_size,
            },
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    print(f"captured {len(frames)} frames, {len(lines) - 1} elements in {seconds:.2f}s: {display}")


# Layout, in the SVG's own units. The picture is 1000 by 590.
WIDTH, HEIGHT = 1000, 590
DESK = (624, 24, 352, 542)  # the miniature desktop: x, y, width, height
CALC_H = 452
LINE = 31
TOTAL = 13.0  # seconds; the animation plays once and rests on the result
ORANGE = "#E06C20"  # the overlay's own colour, overlay._ORANGE


def build() -> None:
    data = json.loads((CAPTURE / "capture.json").read_text(encoding="utf-8"))

    def image(name: str) -> str:
        encoded = base64.b64encode((CAPTURE / name).read_bytes()).decode("ascii")
        return f"data:image/png;base64,{encoded}"

    frame_w, frame_h = data["frame"]
    scale = CALC_H / frame_h
    calc_w = frame_w * scale
    calc_x = DESK[0] + (DESK[2] - calc_w) / 2
    calc_y = DESK[1] + 62
    dialog_w, dialog_h = data["dialog"]
    dialog_scale = (DESK[2] - 28) / dialog_w
    dialog_x = DESK[0] + 14
    dialog_y = DESK[1] + (DESK[3] - dialog_h * dialog_scale) / 2

    # The script: when each line of the transcript appears, and each click lands.
    clicks = [6.35, 7.75, 9.15, 10.55]
    calls = [5.6, 7.0, 8.4, 9.8]
    transcript: list[tuple[float, str, str]] = [
        (0.3, "call", "snapshot(calculator)"),
        (0.9, "note", "first touch: the owner is asked"),
        (3.5, "note", "owner said yes, grant saved"),
        (3.9, "data", data["header"]),
    ]
    for index, step in enumerate(data["steps"]):
        transcript.append((4.1 + index * 0.06, "tree", step["line"]))
    transcript.append((4.4, "note", f"{data['elements']} elements in {data['seconds']} s"))
    for at, step in zip(calls, data["steps"], strict=True):
        transcript.append((at, "call", f"click({step['ref']})"))
    transcript.append((11.3, "call", "snapshot(calculator)"))
    transcript.append((11.9, "result", data["display"]))

    def styled(kind: str, text: str) -> str:
        body = escape(text)
        if kind == "call":
            return f'<tspan class="accent">&gt; </tspan><tspan class="call">{body}</tspan>'
        if kind in ("tree", "result") and "[" in text:
            name, ref = text.rsplit(" [", 1)
            return (
                f'<tspan class="{kind}">  {escape(name)} </tspan>'
                f'<tspan class="accent">[{escape(ref)}</tspan>'
            )
        return f'<tspan class="{kind}">  {body}</tspan>'

    rows = "\n".join(
        f'<text class="row" x="44" y="{92 + index * LINE}" xml:space="preserve" '
        f'style="animation-delay:{at}s">{styled(kind, text)}</text>'
        for index, (at, kind, text) in enumerate(transcript)
    )

    points = [(calc_x + step["x"] * calc_w, calc_y + step["y"] * CALC_H) for step in data["steps"]]
    start = (DESK[0] + DESK[2] - 40, DESK[1] + DESK[3] - 36)
    stops = [(0.0, start, 0), (5.4, start, 0), (5.7, start, 1)]
    for index, point in enumerate(points):
        stops.append((clicks[index] - 0.05, point, 1))  # arrive
        if index + 1 < len(points):
            stops.append((calls[index + 1] + 0.1, point, 1))  # rest until the next call
    stops.append((TOTAL, points[-1], 1))
    # The pointer rests 7 units off each target, beside the glyph and not over it.
    pointer_frames = "\n".join(
        f"{at / TOTAL * 100:.2f}%{{transform:translate({x + 7:.1f}px,{y + 7:.1f}px);"
        f"opacity:{alpha};animation-timing-function:var(--ease-move)}}"
        for at, (x, y), alpha in stops
    )
    ripples = "\n".join(
        f'<circle class="ripple" cx="{x:.1f}" cy="{y:.1f}" r="13" style="animation-delay:{at}s"/>'
        for at, (x, y) in zip(clicks, points, strict=True)
    )
    frames = "\n".join(
        f'<image class="frame" href="{image(f"frame{index}.png")}" width="{frame_w}" '
        f'height="{frame_h}" style="animation-delay:{at + 0.1}s"/>'
        for index, at in enumerate([-1.0, *clicks])
    )
    yes_x = dialog_x + 423 * dialog_scale
    yes_y = dialog_y + 344 * dialog_scale
    label = "Claude is controlling this PC.  Ctrl+Alt+Backspace stops it."
    dx, dy, dw, dh = DESK

    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {WIDTH} {HEIGHT}" role="img"
  aria-labelledby="title desc">
<title id="title">Reach driving Windows Calculator</title>
<desc id="desc">A transcript on the left: a snapshot call, the owner allowing the app at a
Windows dialog, four tree lines with refs, four clicks by ref, and a last snapshot reading
the display as 12. On the right the real Calculator window, with Reach's orange border
around the desktop while the pointer clicks 7, plus, 5 and equals.</desc>
<style>
:root{{--ease:cubic-bezier(.25,.46,.45,.94);--ease-move:cubic-bezier(.45,0,.55,1)}}
text{{font-family:ui-monospace,SFMono-Regular,"Cascadia Mono",Consolas,monospace;font-size:16px}}
.sans{{font-family:"Segoe UI",system-ui,-apple-system,sans-serif}}
.call{{fill:#e8edf3;font-weight:600}}.note{{fill:#77828f}}.data{{fill:#a6b0bc}}
.tree{{fill:#a6b0bc}}.result{{fill:#fff;font-weight:600}}.accent{{fill:{ORANGE}}}
.row{{animation:rise .32s var(--ease) both}}
.frame{{animation:show .2s var(--ease) both}}
.ripple{{fill:none;stroke:{ORANGE};stroke-width:2.5;transform-box:fill-box;
  transform-origin:center;animation:ripple .45s var(--ease) both}}
.dialog{{transform-box:fill-box;transform-origin:center;animation:dialog 2.5s var(--ease) 1s both}}
.overlay{{animation:hold 7.3s var(--ease) 5.6s both}}
.pointer{{animation:pointer {TOTAL}s linear both}}
@keyframes rise{{from{{opacity:0;transform:translateY(6px)}}to{{opacity:1;transform:none}}}}
@keyframes show{{from{{opacity:0}}to{{opacity:1}}}}
@keyframes ripple{{0%{{opacity:0;transform:scale(.5)}}8%{{opacity:.9;transform:scale(.5)}}
  100%{{opacity:0;transform:scale(1.7)}}}}
@keyframes dialog{{0%{{opacity:0;transform:scale(.96)}}13%,94%{{opacity:1;transform:none}}
  100%{{opacity:0;transform:scale(.98)}}}}
@keyframes hold{{0%,100%{{opacity:0}}4%,96%{{opacity:1}}}}
@keyframes pointer{{
{pointer_frames}
}}
@media (prefers-reduced-motion:reduce){{
  .row,.frame,.ripple,.dialog,.overlay,.pointer{{animation-duration:.01s;animation-delay:.01s!important}}
}}
</style>
<defs>
  <clipPath id="calc">
    <rect x="11" y="1" width="{frame_w - 22}" height="{frame_h - 13}" rx="10"/>
  </clipPath>
  <clipPath id="box">
    <rect x="10" y="0" width="{dialog_w - 20}" height="{dialog_h - 10}" rx="10"/>
  </clipPath>
</defs>
<rect width="{WIDTH}" height="{HEIGHT}" rx="14" fill="#0d1117"/>
<rect x="24" y="24" width="576" height="542" rx="10" fill="#11161d" stroke="#232b36"/>
<text class="sans" x="44" y="55" fill="#77828f" font-size="13">MCP client  →  reach</text>
<line x1="24" y1="68" x2="600" y2="68" stroke="#232b36"/>
{rows}
<rect x="{dx}" y="{dy}" width="{dw}" height="{dh}" rx="10" fill="#1a2330" stroke="#232b36"/>
<g transform="translate({calc_x:.1f} {calc_y:.1f}) scale({scale:.4f})" clip-path="url(#calc)">
{frames}
</g>
<g class="overlay">
  <rect x="{dx + 2}" y="{dy + 2}" width="{dw - 4}" height="{dh - 4}" rx="9" fill="none"
    stroke="{ORANGE}" stroke-width="4"/>
  <rect x="{dx + 14}" y="{dy + 2}" width="{dw - 28}" height="24" fill="{ORANGE}"/>
  <text class="sans" x="{dx + dw / 2}" y="{dy + 18.5}" fill="#fff" font-size="10.4"
    text-anchor="middle" textLength="{dw - 48}" lengthAdjust="spacingAndGlyphs">{label}</text>
</g>
<g class="dialog">
  <g transform="translate({dialog_x:.1f} {dialog_y:.1f}) scale({dialog_scale:.4f})"
    clip-path="url(#box)">
    <image href="{image("dialog.png")}" width="{dialog_w}" height="{dialog_h}"/>
  </g>
</g>
<circle class="ripple" cx="{yes_x:.1f}" cy="{yes_y:.1f}" r="13" style="animation-delay:2.85s"/>
{ripples}
<g class="pointer">
  <path d="M0 0v17l4.6-4.4 3 7 2.6-1.1-3-6.9h6.3z" fill="#fff" stroke="#0d1117" stroke-width="1.2"
    stroke-linejoin="round"/>
</g>
</svg>
"""
    (ASSETS / "hero.svg").write_text(svg, encoding="utf-8")
    print(f"wrote docs/assets/hero.svg, {len(svg) // 1024} KB, {TOTAL:.0f} s, {WIDTH}x{HEIGHT}")


if __name__ == "__main__":
    if "--reuse" not in sys.argv:
        capture()
    build()
