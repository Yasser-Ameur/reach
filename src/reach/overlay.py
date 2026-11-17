"""One thread that owns the kill hotkey and the overlay shown while Reach sends input."""

import ctypes
import threading
from collections.abc import Callable
from ctypes import wintypes

from reach.win32 import HANDLE, HWND, gdi32, kernel32, user32

_LABEL = "Claude is controlling this PC.  Ctrl+Alt+Backspace stops it."
_KEY_COLOUR = 0x00FF00FF  # painted nowhere else, so it becomes the transparent colour
_ORANGE = 0x00206CE0  # 0x00BBGGRR
_BORDER = 6
_HOLD_MS = 2000
_WM_PAINT, _WM_TIMER, _WM_HOTKEY, _WM_SHOW = 0x000F, 0x0113, 0x0312, 0x8000

_WNDPROC = ctypes.WINFUNCTYPE(
    ctypes.c_ssize_t, HWND, wintypes.UINT, wintypes.WPARAM, wintypes.LPARAM
)


class _WndClass(ctypes.Structure):
    _fields_ = (
        ("style", wintypes.UINT),
        ("lpfnWndProc", _WNDPROC),
        ("cbClsExtra", ctypes.c_int),
        ("cbWndExtra", ctypes.c_int),
        ("hInstance", HANDLE),
        ("hIcon", HANDLE),
        ("hCursor", HANDLE),
        ("hbrBackground", HANDLE),
        ("lpszMenuName", wintypes.LPCWSTR),
        ("lpszClassName", wintypes.LPCWSTR),
    )


class _PaintStruct(ctypes.Structure):
    _fields_ = (
        ("hdc", HANDLE),
        ("fErase", wintypes.BOOL),
        ("rcPaint", wintypes.RECT),
        ("fRestore", wintypes.BOOL),
        ("fIncUpdate", wintypes.BOOL),
        ("rgbReserved", ctypes.c_byte * 32),
    )


_RECT_P = ctypes.POINTER(wintypes.RECT)
user32.DefWindowProcW.argtypes = [HWND, wintypes.UINT, wintypes.WPARAM, wintypes.LPARAM]
user32.DefWindowProcW.restype = ctypes.c_ssize_t
user32.RegisterClassW.argtypes = [ctypes.POINTER(_WndClass)]
user32.CreateWindowExW.argtypes = [
    wintypes.DWORD,
    wintypes.LPCWSTR,
    wintypes.LPCWSTR,
    wintypes.DWORD,
    *[ctypes.c_int] * 4,
    HWND,
    HANDLE,
    HANDLE,
    ctypes.c_void_p,
]
user32.CreateWindowExW.restype = HWND
user32.SetLayeredWindowAttributes.argtypes = [HWND, wintypes.DWORD, ctypes.c_byte, wintypes.DWORD]
user32.RegisterHotKey.argtypes = [HWND, ctypes.c_int, wintypes.UINT, wintypes.UINT]
user32.GetMessageW.argtypes = [ctypes.POINTER(wintypes.MSG), HWND, wintypes.UINT, wintypes.UINT]
user32.DispatchMessageW.argtypes = [ctypes.POINTER(wintypes.MSG)]
user32.PostThreadMessageW.argtypes = [
    wintypes.DWORD,
    wintypes.UINT,
    wintypes.WPARAM,
    wintypes.LPARAM,
]
user32.SetTimer.argtypes = [HWND, ctypes.c_size_t, wintypes.UINT, ctypes.c_void_p]
user32.KillTimer.argtypes = [HWND, ctypes.c_size_t]
user32.BeginPaint.argtypes = [HWND, ctypes.POINTER(_PaintStruct)]
user32.BeginPaint.restype = HANDLE
user32.EndPaint.argtypes = [HWND, ctypes.POINTER(_PaintStruct)]
user32.GetClientRect.argtypes = [HWND, _RECT_P]
user32.FillRect.argtypes = [HANDLE, _RECT_P, HANDLE]
user32.DrawTextW.argtypes = [HANDLE, wintypes.LPCWSTR, ctypes.c_int, _RECT_P, wintypes.UINT]
gdi32.CreateSolidBrush.argtypes = [wintypes.DWORD]
gdi32.CreateSolidBrush.restype = HANDLE
gdi32.SetBkMode.argtypes = [HANDLE, ctypes.c_int]
gdi32.SetTextColor.argtypes = [HANDLE, wintypes.DWORD]
kernel32.GetModuleHandleW.argtypes = [wintypes.LPCWSTR]
kernel32.GetModuleHandleW.restype = HANDLE


class Overlay:
    def __init__(self, on_kill: Callable[[], None]) -> None:
        self._on_kill = on_kill
        self._ready = threading.Event()
        self._hotkey_ok = False
        self._thread_id = 0

    def start(self) -> None:
        """Raises RuntimeError when the kill hotkey is taken: no kill switch, no server."""
        threading.Thread(target=self._run, daemon=True, name="reach-overlay").start()
        self._ready.wait()
        if not self._hotkey_ok:
            raise RuntimeError("Ctrl+Alt+Backspace is taken by another program; Reach will not run")

    def show(self) -> None:
        """Show the overlay now and hide it two seconds after the last call."""
        user32.PostThreadMessageW(self._thread_id, _WM_SHOW, 0, 0)

    def _paint(self, hwnd: int) -> None:
        paint, area = _PaintStruct(), wintypes.RECT()
        hdc = user32.BeginPaint(hwnd, ctypes.byref(paint))
        user32.GetClientRect(hwnd, ctypes.byref(area))
        brush = gdi32.CreateSolidBrush(_ORANGE)
        # The window spans every monitor; the label sits on the primary one.
        middle = user32.GetSystemMetrics(0) // 2 - user32.GetSystemMetrics(76)
        top = -user32.GetSystemMetrics(77)
        for box in (
            (0, 0, area.right, _BORDER),
            (0, area.bottom - _BORDER, area.right, area.bottom),
            (0, 0, _BORDER, area.bottom),
            (area.right - _BORDER, 0, area.right, area.bottom),
            (middle - 300, top, middle + 300, top + 34),
        ):
            user32.FillRect(hdc, ctypes.byref(wintypes.RECT(*box)), brush)
        gdi32.SetBkMode(hdc, 1)  # TRANSPARENT
        gdi32.SetTextColor(hdc, 0x00FFFFFF)
        label = wintypes.RECT(middle - 300, top, middle + 300, top + 34)
        user32.DrawTextW(hdc, _LABEL, -1, ctypes.byref(label), 0x25)  # centred, one line
        gdi32.DeleteObject(brush)
        user32.EndPaint(hwnd, ctypes.byref(paint))

    def _run(self) -> None:
        self._thread_id = kernel32.GetCurrentThreadId()
        # Ctrl+Alt, no auto repeat, Backspace.
        self._hotkey_ok = bool(user32.RegisterHotKey(None, 1, 0x0001 | 0x0002 | 0x4000, 0x08))

        def wndproc(hwnd: int, message: int, wparam: int, lparam: int) -> int:
            if message == _WM_PAINT:
                self._paint(hwnd)
                return 0
            if message == _WM_TIMER:
                user32.KillTimer(hwnd, 1)
                user32.ShowWindow(hwnd, 0)
                return 0
            return int(user32.DefWindowProcW(hwnd, message, wparam, lparam))

        instance = kernel32.GetModuleHandleW(None)
        window_class = _WndClass(
            lpfnWndProc=_WNDPROC(wndproc),
            hInstance=instance,
            hbrBackground=gdi32.CreateSolidBrush(_KEY_COLOUR),
            lpszClassName="ReachOverlay",
        )
        user32.RegisterClassW(ctypes.byref(window_class))
        # Layered, click-through, topmost, never activated, absent from the taskbar.
        ex_style = 0x00080000 | 0x00000020 | 0x00000008 | 0x08000000 | 0x00000080
        hwnd = user32.CreateWindowExW(
            ex_style,
            "ReachOverlay",
            "",
            0x80000000,  # WS_POPUP
            *(user32.GetSystemMetrics(index) for index in (76, 77, 78, 79)),  # all monitors
            None,
            None,
            instance,
            None,
        )
        user32.SetLayeredWindowAttributes(hwnd, _KEY_COLOUR, 0, 1)  # LWA_COLORKEY
        self._ready.set()

        message = wintypes.MSG()
        while user32.GetMessageW(ctypes.byref(message), None, 0, 0) > 0:
            if message.message == _WM_HOTKEY:
                self._on_kill()
                user32.ShowWindow(hwnd, 0)
            elif message.message == _WM_SHOW:
                user32.ShowWindow(hwnd, 4)  # SW_SHOWNOACTIVATE
                user32.SetTimer(hwnd, 1, _HOLD_MS, None)
            else:
                user32.DispatchMessageW(ctypes.byref(message))
