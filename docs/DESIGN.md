# Reach design

One Python process speaking MCP over stdio. No daemon, no state beyond two files in `~/.reach`.

```
server.py    tool definitions; each tool is guard check, act, log
guard.py     grants, denials, kill flag, action log. Pure Python
tree.py      element tree to text with refs. Pure Python
keys.py      "ctrl+s" to virtual key codes; refuses shell and paste combinations. Pure Python
png.py       raw pixels to PNG with zlib. Pure Python
win32.py     ctypes: windows, processes, SendInput, PrintWindow, MessageBox
uia.py       comtypes: UI Automation tree and focus
overlay.py   one thread owning the hotkey, the shared kill counter and the overlay window
```

Decisions:

- Tree first, pixels second. A snapshot is text and costs a fraction of an image; a ref names an element exactly. `screenshot` and x, y stay for apps with a poor tree.
- Clicks are real input at the element's centre, sent with `SendInput`. One path for refs and coordinates, and the guard can check what sits under the point.
- Screenshots use `PrintWindow`, so a window is captured even when covered and nothing else on screen can leak into the image.
- The kill switch is terminal. A resume path is one more thing a steered model could ask the owner to use.
- A hotkey belongs to one process, and every MCP client session starts its own server. So servers share the kill switch: the holder of the hotkey bumps a counter in shared memory that all of them poll, and the others keep trying to take the hotkey in case the holder exits. A counter and not a signal, so there is nothing to clear and a server started later is never stopped by an old press. A server still refuses to start when the hotkey is held by something that is not Reach.
- `~/.reach` and not AppData, because packaged MCP clients see a virtualised AppData.

Rejected: calling UI Automation patterns (`Invoke`, `SetValue`) in place of real input. It works on background windows and needs no focus, but each control type needs its own pattern, many custom controls expose none, and an action that never moves the pointer is invisible to the owner watching. Trade-off taken: Reach must bring the window forward and is slower, in exchange for one input path the owner can see and stop.
