"""A small native window for the live check: a text field, a password field, a button."""

import ctypes
from ctypes import wintypes

user32 = ctypes.WinDLL("user32")
user32.CreateWindowExW.argtypes = [
    wintypes.DWORD,
    wintypes.LPCWSTR,
    wintypes.LPCWSTR,
    wintypes.DWORD,
    *[ctypes.c_int] * 4,
    wintypes.HWND,
    wintypes.HANDLE,
    wintypes.HANDLE,
    ctypes.c_void_p,
]
user32.CreateWindowExW.restype = wintypes.HWND
user32.GetMessageW.argtypes = [
    ctypes.POINTER(wintypes.MSG),
    wintypes.HWND,
    wintypes.UINT,
    wintypes.UINT,
]
user32.IsDialogMessageW.argtypes = [wintypes.HWND, ctypes.POINTER(wintypes.MSG)]
user32.DispatchMessageW.argtypes = [ctypes.POINTER(wintypes.MSG)]

CHILD = 0x40000000 | 0x10000000 | 0x00010000  # WS_CHILD, WS_VISIBLE, WS_TABSTOP
BORDER = 0x00800000

# "#32770" is the built in dialog class, so no window class has to be registered.
top = user32.CreateWindowExW(
    0, "#32770", "Reach target", 0x00CF0000 | 0x10000000, 200, 200, 420, 220, None, None, None, None
)
user32.CreateWindowExW(0, "EDIT", "", CHILD | BORDER, 20, 20, 360, 28, top, None, None, None)
user32.CreateWindowExW(0, "EDIT", "", CHILD | BORDER | 0x20, 20, 60, 360, 28, top, None, None, None)
user32.CreateWindowExW(0, "BUTTON", "Press", CHILD, 20, 100, 120, 32, top, None, None, None)

message = wintypes.MSG()
while user32.GetMessageW(ctypes.byref(message), None, 0, 0) > 0:
    if not user32.IsDialogMessageW(top, ctypes.byref(message)):
        user32.DispatchMessageW(ctypes.byref(message))
