"""The Win32 calls Reach needs, through ctypes: windows, processes, input, capture."""

import ctypes
import threading
import time
from ctypes import wintypes

from reach.guard import App, Refused
from reach.keys import EXTENDED
from reach.tree import Rect

user32 = ctypes.WinDLL("user32", use_last_error=True)
gdi32 = ctypes.WinDLL("gdi32", use_last_error=True)
kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
advapi32 = ctypes.WinDLL("advapi32", use_last_error=True)
dwmapi = ctypes.WinDLL("dwmapi")

HANDLE = wintypes.HANDLE
HWND = wintypes.HWND
DWORD = wintypes.DWORD
BOOL = wintypes.BOOL

_ENUM_PROC = ctypes.WINFUNCTYPE(BOOL, HWND, wintypes.LPARAM)

# Handles are 64 bit; without these signatures ctypes truncates them to int.
user32.EnumWindows.argtypes = [_ENUM_PROC, wintypes.LPARAM]
user32.EnumChildWindows.argtypes = [HWND, _ENUM_PROC, wintypes.LPARAM]
user32.IsWindowVisible.argtypes = [HWND]
user32.IsIconic.argtypes = [HWND]
user32.ShowWindow.argtypes = [HWND, ctypes.c_int]
user32.GetWindowTextW.argtypes = [HWND, wintypes.LPWSTR, ctypes.c_int]
user32.GetWindowThreadProcessId.argtypes = [HWND, ctypes.POINTER(DWORD)]
user32.GetWindowThreadProcessId.restype = DWORD
user32.GetWindowRect.argtypes = [HWND, ctypes.POINTER(wintypes.RECT)]
user32.WindowFromPoint.argtypes = [wintypes.POINT]
user32.WindowFromPoint.restype = HWND
user32.GetAncestor.argtypes = [HWND, wintypes.UINT]
user32.GetAncestor.restype = HWND
user32.GetForegroundWindow.restype = HWND
user32.SetForegroundWindow.argtypes = [HWND]
user32.AttachThreadInput.argtypes = [DWORD, DWORD, BOOL]
user32.GetDC.argtypes = [HWND]
user32.GetDC.restype = HANDLE
user32.ReleaseDC.argtypes = [HWND, HANDLE]
user32.PrintWindow.argtypes = [HWND, HANDLE, wintypes.UINT]
user32.MessageBoxW.argtypes = [HWND, wintypes.LPCWSTR, wintypes.LPCWSTR, wintypes.UINT]
user32.SetProcessDpiAwarenessContext.argtypes = [HANDLE]
user32.GetThreadDpiAwarenessContext.restype = HANDLE
user32.GetAwarenessFromDpiAwarenessContext.argtypes = [HANDLE]
user32.GetClassNameW.argtypes = [HWND, wintypes.LPWSTR, ctypes.c_int]
user32.GetWindowDpiAwarenessContext.argtypes = [HWND]
user32.GetWindowDpiAwarenessContext.restype = HANDLE
user32.SetThreadDpiAwarenessContext.argtypes = [HANDLE]
user32.SetThreadDpiAwarenessContext.restype = HANDLE
gdi32.CreateCompatibleDC.argtypes = [HANDLE]
gdi32.CreateCompatibleDC.restype = HANDLE
gdi32.CreateCompatibleBitmap.argtypes = [HANDLE, ctypes.c_int, ctypes.c_int]
gdi32.CreateCompatibleBitmap.restype = HANDLE
gdi32.SelectObject.argtypes = [HANDLE, HANDLE]
gdi32.SelectObject.restype = HANDLE
gdi32.DeleteObject.argtypes = [HANDLE]
gdi32.DeleteDC.argtypes = [HANDLE]
gdi32.SetStretchBltMode.argtypes = [HANDLE, ctypes.c_int]
gdi32.StretchBlt.argtypes = [HANDLE] + [ctypes.c_int] * 4 + [HANDLE] + [ctypes.c_int] * 4 + [DWORD]
gdi32.GetDIBits.argtypes = [
    HANDLE,
    HANDLE,
    wintypes.UINT,
    wintypes.UINT,
    ctypes.c_void_p,
    ctypes.c_void_p,
    wintypes.UINT,
]
kernel32.OpenProcess.argtypes = [DWORD, BOOL, DWORD]
kernel32.OpenProcess.restype = HANDLE
kernel32.CloseHandle.argtypes = [HANDLE]
kernel32.QueryFullProcessImageNameW.argtypes = [
    HANDLE,
    DWORD,
    wintypes.LPWSTR,
    ctypes.POINTER(DWORD),
]
kernel32.GetCurrentThreadId.restype = DWORD
advapi32.OpenProcessToken.argtypes = [HANDLE, DWORD, ctypes.POINTER(HANDLE)]
advapi32.GetTokenInformation.argtypes = [
    HANDLE,
    ctypes.c_int,
    ctypes.c_void_p,
    DWORD,
    ctypes.POINTER(DWORD),
]
dwmapi.DwmGetWindowAttribute.argtypes = [HWND, DWORD, ctypes.c_void_p, DWORD]


class _MouseInput(ctypes.Structure):
    _fields_ = (
        ("dx", wintypes.LONG),
        ("dy", wintypes.LONG),
        ("mouseData", DWORD),
        ("dwFlags", DWORD),
        ("time", DWORD),
        ("dwExtraInfo", ctypes.c_size_t),
    )


class _KeybdInput(ctypes.Structure):
    _fields_ = (
        ("wVk", wintypes.WORD),
        ("wScan", wintypes.WORD),
        ("dwFlags", DWORD),
        ("time", DWORD),
        ("dwExtraInfo", ctypes.c_size_t),
    )


class _InputUnion(ctypes.Union):
    _fields_ = (("mi", _MouseInput), ("ki", _KeybdInput))


class _Input(ctypes.Structure):
    _fields_ = (("type", DWORD), ("u", _InputUnion))


class _BitmapInfoHeader(ctypes.Structure):
    _fields_ = (
        ("biSize", DWORD),
        ("biWidth", wintypes.LONG),
        ("biHeight", wintypes.LONG),
        ("biPlanes", wintypes.WORD),
        ("biBitCount", wintypes.WORD),
        ("biCompression", DWORD),
        ("biSizeImage", DWORD),
        ("biXPelsPerMeter", wintypes.LONG),
        ("biYPelsPerMeter", wintypes.LONG),
        ("biClrUsed", DWORD),
        ("biClrImportant", DWORD),
    )


user32.SendInput.argtypes = [wintypes.UINT, ctypes.POINTER(_Input), ctypes.c_int]

_KEYUP, _UNICODE, _EXTENDEDKEY = 0x0002, 0x0004, 0x0001
_BUTTONS = {"left": (0x0002, 0x0004), "right": (0x0008, 0x0010), "middle": (0x0020, 0x0040)}
_WHEEL, _HWHEEL = 0x0800, 0x1000
_FRAME_HOST = "applicationframehost.exe"


killed = threading.Event()  # the server points this at the guard's kill flag


def init() -> None:
    """Per monitor DPI awareness, so every coordinate is a physical pixel. Without it
    Windows hands back scaled coordinates and clicks land in the wrong place."""
    user32.SetProcessDpiAwarenessContext(HANDLE(-4))
    context = user32.GetThreadDpiAwarenessContext()
    if user32.GetAwarenessFromDpiAwarenessContext(context) != 2:  # per monitor
        raise RuntimeError("could not make the process per monitor DPI aware")


def _pid(hwnd: int) -> int:
    pid = DWORD()
    user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
    return pid.value


def _process(pid: int) -> App | None:
    """The app behind a pid, or None when it cannot be inspected or runs elevated."""
    process = kernel32.OpenProcess(0x1000, False, pid)  # PROCESS_QUERY_LIMITED_INFORMATION
    if not process:
        return None
    try:
        token = HANDLE()
        if not advapi32.OpenProcessToken(process, 0x0008, ctypes.byref(token)):  # TOKEN_QUERY
            return None
        try:
            elevated, size = DWORD(), DWORD()
            ok = advapi32.GetTokenInformation(  # 20 is TokenElevation
                token, 20, ctypes.byref(elevated), ctypes.sizeof(elevated), ctypes.byref(size)
            )
            if not ok or elevated.value:
                return None
        finally:
            kernel32.CloseHandle(token)
        buffer = ctypes.create_unicode_buffer(1024)
        length = DWORD(len(buffer))
        if not kernel32.QueryFullProcessImageNameW(process, 0, buffer, ctypes.byref(length)):
            return None
        return App(path=buffer.value.lower(), pid=pid)
    finally:
        kernel32.CloseHandle(process)


def _children(hwnd: int) -> list[int]:
    found: list[int] = []

    def collect(child: int, _: int) -> bool:
        found.append(child)
        return True

    user32.EnumChildWindows(hwnd, _ENUM_PROC(collect), 0)
    return found


def app_of(hwnd: int) -> App | None:
    """The app that owns a top level window. A packaged app's frame is owned by a
    shared host process, so the real app is the owner of the frame's core window.
    Any other foreign child (an input helper, a web view) is not the app."""
    host_pid = _pid(hwnd)
    app = _process(host_pid)
    if app is None or app.name != _FRAME_HOST:
        return app
    name = ctypes.create_unicode_buffer(64)
    for child in _children(hwnd):
        user32.GetClassNameW(child, name, len(name))
        if name.value == "Windows.UI.Core.CoreWindow" and _pid(child) != host_pid:
            return _process(_pid(child))
    return None


def windows() -> list[tuple[int, str]]:
    """Handle and title of every visible, titled, uncloaked top level window."""
    found: list[tuple[int, str]] = []

    def collect(hwnd: int, _: int) -> bool:
        cloaked = DWORD()
        dwmapi.DwmGetWindowAttribute(hwnd, 14, ctypes.byref(cloaked), ctypes.sizeof(cloaked))
        title = ctypes.create_unicode_buffer(256)
        user32.GetWindowTextW(hwnd, title, len(title))
        if user32.IsWindowVisible(hwnd) and title.value and not cloaked.value:
            found.append((hwnd, title.value))
        return True

    user32.EnumWindows(_ENUM_PROC(collect), 0)
    return found


def rect_of(hwnd: int) -> Rect:
    rect = wintypes.RECT()
    if not user32.GetWindowRect(hwnd, ctypes.byref(rect)):
        raise OSError(f"window {hwnd} does not exist")
    return rect.left, rect.top, rect.right, rect.bottom


def root_at(x: int, y: int) -> int:
    return int(user32.GetAncestor(user32.WindowFromPoint(wintypes.POINT(x, y)), 2) or 0)


def foreground() -> int:
    return int(user32.GetForegroundWindow() or 0)


def focus(hwnd: int) -> None:
    """Bring a window forward. Windows only lets the foreground thread hand focus
    over, so attach to it for the call; no key is sent to the window losing focus."""
    if user32.IsIconic(hwnd):
        user32.ShowWindow(hwnd, 9)  # SW_RESTORE
    if foreground() == hwnd:
        return
    ours = kernel32.GetCurrentThreadId()
    theirs = user32.GetWindowThreadProcessId(foreground(), None)
    user32.AttachThreadInput(ours, theirs, True)
    user32.SetForegroundWindow(hwnd)
    user32.AttachThreadInput(ours, theirs, False)
    for _ in range(20):  # the switch is asynchronous; give it half a second
        if foreground() == hwnd:
            return
        time.sleep(0.025)


def _send(*inputs: _Input) -> None:
    # Checked at the last step, so the kill switch also stops a call already running.
    if killed.is_set():
        raise Refused("the kill switch was pressed. Restart the Reach server to continue.")
    array = (_Input * len(inputs))(*inputs)
    if user32.SendInput(len(inputs), array, ctypes.sizeof(_Input)) != len(inputs):
        raise OSError("Windows blocked the input")


def _mouse(flags: int, data: int = 0) -> _Input:
    return _Input(type=0, u=_InputUnion(mi=_MouseInput(mouseData=data & 0xFFFFFFFF, dwFlags=flags)))


def _key(vk: int, flags: int, scan: int = 0) -> _Input:
    return _Input(type=1, u=_InputUnion(ki=_KeybdInput(wVk=vk, wScan=scan, dwFlags=flags)))


def click(x: int, y: int, button: str, double: bool) -> None:
    down, up = _BUTTONS[button]
    user32.SetCursorPos(x, y)
    _send(*[_mouse(down), _mouse(up)] * (2 if double else 1))


def scroll(x: int, y: int, notches: int, horizontal: bool) -> None:
    user32.SetCursorPos(x, y)
    _send(_mouse(_HWHEEL if horizontal else _WHEEL, notches * 120))


def send_text(text: str) -> None:
    for line_number, line in enumerate(text.split("\n")):
        if line_number:
            send_keys([0x0D])
        units = line.encode("utf-16-le")
        for i in range(0, len(units), 2):
            unit = int.from_bytes(units[i : i + 2], "little")
            _send(_key(0, _UNICODE, unit), _key(0, _UNICODE | _KEYUP, unit))


def send_keys(codes: list[int]) -> None:
    def flags(vk: int) -> int:
        return _EXTENDEDKEY if vk in EXTENDED else 0

    _send(
        *[_key(vk, flags(vk)) for vk in codes],
        *[_key(vk, flags(vk) | _KEYUP) for vk in reversed(codes)],
    )


def capture(hwnd: int, max_side: int) -> tuple[int, int, bytes, float]:
    """Width, height, top-down BGRA pixels and the scale applied, for one window.
    PrintWindow asks the window to draw itself, so nothing covering it is captured."""
    left, top, right, bottom = rect_of(hwnd)
    if right <= left or bottom <= top:
        raise OSError("the window has no area; it may be minimized")
    # A window that is not DPI aware draws itself smaller than it appears on screen.
    # Capture at the size it draws, and report the scale against its size on screen,
    # so screenshot pixels still map back to screen pixels.
    ours = user32.SetThreadDpiAwarenessContext(user32.GetWindowDpiAwarenessContext(hwnd))
    try:
        drawn = rect_of(hwnd)
    finally:
        user32.SetThreadDpiAwarenessContext(ours)
    width, height = drawn[2] - drawn[0], drawn[3] - drawn[1]
    on_screen_w, on_screen_h = right - left, bottom - top
    scale = min(1.0, max_side / max(on_screen_w, on_screen_h), width / on_screen_w)
    out_w, out_h = max(1, round(on_screen_w * scale)), max(1, round(on_screen_h * scale))
    screen = user32.GetDC(None)
    full_dc, small_dc = gdi32.CreateCompatibleDC(screen), gdi32.CreateCompatibleDC(screen)
    full = gdi32.CreateCompatibleBitmap(screen, width, height)
    small = gdi32.CreateCompatibleBitmap(screen, out_w, out_h)
    try:
        gdi32.SelectObject(full_dc, full)
        stock = gdi32.SelectObject(small_dc, small)
        if not user32.PrintWindow(hwnd, full_dc, 2):  # PW_RENDERFULLCONTENT
            raise OSError("the window did not draw itself; it may be hung")
        gdi32.SetStretchBltMode(small_dc, 4)  # HALFTONE
        gdi32.StretchBlt(small_dc, 0, 0, out_w, out_h, full_dc, 0, 0, width, height, 0x00CC0020)
        header = _BitmapInfoHeader(
            biSize=ctypes.sizeof(_BitmapInfoHeader),
            biWidth=out_w,
            biHeight=-out_h,  # negative: rows come top first
            biPlanes=1,
            biBitCount=32,
        )
        pixels = ctypes.create_string_buffer(out_w * out_h * 4)
        gdi32.SelectObject(small_dc, stock)  # GetDIBits wants the bitmap deselected
        if not gdi32.GetDIBits(screen, small, 0, out_h, pixels, ctypes.byref(header), 0):
            raise OSError("could not read the window's pixels")
        return out_w, out_h, pixels.raw, scale
    finally:
        gdi32.DeleteDC(full_dc)
        gdi32.DeleteDC(small_dc)
        gdi32.DeleteObject(full)
        gdi32.DeleteObject(small)
        user32.ReleaseDC(None, screen)


def ask(text: str) -> bool:
    """A system modal Yes or No box, No by default. True only on Yes.

    The box takes focus, and Y answers it, so an owner typing in another window when
    it appears could grant by accident. A yes inside the first second is therefore
    not believed and the box is shown again; the stray keys after it hit No."""
    flags = 0x4 | 0x30 | 0x100 | 0x1000 | 0x10000  # YESNO, WARNING, DEFBUTTON2, SYSTEMMODAL, FG
    while True:
        shown = time.monotonic()
        if user32.MessageBoxW(None, text, "Reach", flags) != 6:
            return False
        if time.monotonic() - shown >= 1.0:
            return True
