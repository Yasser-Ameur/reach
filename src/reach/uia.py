"""UI Automation through comtypes: one window's element tree, and where focus is."""

import sys
import threading
from _ctypes import COMError
from typing import Any

sys.coinit_flags = 0  # type: ignore[attr-defined]  # multithreaded COM; must be set before comtypes is imported

import comtypes  # noqa: E402
import comtypes.client  # noqa: E402

from reach.tree import Node  # noqa: E402

comtypes.client.GetModule("UIAutomationCore.dll")
from comtypes.gen import UIAutomationClient as _api  # noqa: E402

_ROLES = (  # noqa: SIM905
    "Button Calendar CheckBox ComboBox Edit Hyperlink Image ListItem List Menu MenuBar "
    "MenuItem ProgressBar RadioButton ScrollBar Slider Spinner StatusBar Tab TabItem Text "
    "ToolBar ToolTip Tree TreeItem Custom Group Thumb DataGrid DataItem Document SplitButton "
    "Window Pane Header HeaderItem Table TitleBar Separator SemanticZoom AppBar"
).split()  # control type ids 50000 upward, in order

# ControlType, Name, BoundingRectangle, IsEnabled, IsPassword, IsOffscreen,
# HasKeyboardFocus, Value.Value
_PROPERTIES = (30003, 30005, 30001, 30010, 30019, 30022, 30008, 30045)

_thread = threading.local()
_automation: Any = None


def _uia() -> Any:
    global _automation
    if not getattr(_thread, "ready", False):
        comtypes.CoInitializeEx(0)  # type: ignore[no-untyped-call]
        _thread.ready = True
    if _automation is None:
        _automation = comtypes.client.CreateObject(_api.CUIAutomation, interface=_api.IUIAutomation)
    return _automation


def _node(element: Any) -> Node:
    control_type = element.CachedControlType - 50000
    rect = element.CachedBoundingRectangle
    password = bool(element.CachedIsPassword)
    children = element.GetCachedChildren()
    return Node(
        role=_ROLES[control_type] if 0 <= control_type < len(_ROLES) else "Custom",
        name=element.CachedName or "",
        # A password's value is never read out of the cache, not just hidden later.
        value="" if password else str(element.GetCachedPropertyValue(30045) or ""),
        rect=(rect.left, rect.top, rect.right, rect.bottom),
        enabled=bool(element.CachedIsEnabled),
        focused=bool(element.CachedHasKeyboardFocus),
        password=password,
        offscreen=bool(element.CachedIsOffscreen),
        children=(
            [_node(children.GetElement(i)) for i in range(children.Length)] if children else []
        ),
    )


def snapshot(hwnd: int) -> Node:
    """The whole control view of a window, fetched in one cross process call."""
    uia = _uia()
    request = uia.CreateCacheRequest()
    for property_id in _PROPERTIES:
        request.AddProperty(property_id)
    request.TreeScope = 7  # element, children, descendants
    request.TreeFilter = uia.ControlViewCondition
    root = _node(uia.ElementFromHandleBuildCache(hwnd, request))
    root.offscreen = False  # a window asked for by handle is always rendered
    return root


def focus_is_password() -> bool:
    """True when focus is in a password field, and when focus cannot be read at all."""
    try:
        return bool(_uia().GetFocusedElement().CurrentIsPassword)
    except COMError:
        return True
