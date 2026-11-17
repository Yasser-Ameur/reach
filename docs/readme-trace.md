# README trace (2026-11-17)

No earlier README existed, so there is no audit of old claims.

| Claim | Source |
|---|---|
| The snapshot block in the hero | Output of `scripts/live_check.py` run this session (three TitleBar child lines cut for length) |
| Refs drive click and type; text read back | Live check line "typed text read back from the tree" |
| Screenshot and x, y fallback works | Live check line "click by screenshot pixels landed on the button" |
| Install from a checkout creates `reach.exe` | `pip install -e ".[dev]"` run this session; `.venv\Scripts\reach.exe` started over stdio and listed seven tools |
| `.mcp.json` entry | NOT RUN in a client this session. The stdio launch itself is proven by the row above |
| Every app shows `not granted` at first | stdio run this session: nine windows, all `not granted` |
| Titles only for granted apps | `src/reach/server.py` `windows`; not asserted by a test |
| Tool table | `src/reach/server.py`, one `@server.tool()` each; 800 is `tree.LIMIT`, 1568 is `server.MAX_SIDE` |
| Grant keyed by path, title ignored | `tests/test_reach.py::test_grant_keyed_by_path` |
| Revoke takes effect on the next call | `test_revoking_a_line_takes_effect_without_restart` |
| No is held until restart, one dialog per app | `test_denial_cached` |
| Own windows refused; no call while a dialog is open | `test_own_process_refused`, `test_pending_dialog_blocks_input` |
| Uninspectable process refused | `test_uninspectable_refused`; that an elevated process is uninspectable is `win32._process`, NOT exercised live |
| App under the point and foreground app are checked | `test_tool_click_checks_app_under_point`, `test_tool_keys_check_foreground`; mutation run this session: deleting either check turns that test red |
| Password field: no typing, redacted | Live check line "password field: Refused"; `test_password_value_redacted` |
| Kill switch is final | Live check sent the real hotkey, line "after kill switch: Refused"; `test_killed_refuses_everything` |
| Server does not start without the hotkey | `overlay.Overlay.start` raises; NOT exercised |
| Overlay appears and hides after two seconds | `overlay._HOLD_MS`; shown during the live check, not asserted or captured |
| Every call logged | `test_every_call_logged`; `test_tool_every_call_logged`; live check printed 16 log lines |
| Shell and paste combinations refused | `test_tool_shell_and_paste_combos_refused`; live check line "shell combo: Refused" |
| Old ref matches nothing | `test_tool_old_ref_is_refused`; live check line "stale ref: Refused: s1e2" |
| Kill switch stops typing in flight | `test_kill_stops_input_already_in_flight` |
| Paste through a menu still works | Not tested; stated as a weakness, threat model A6 |
| Gate commands | Run this session, all green |
| No demo GIF or hero image | Deferred until the repository is public |
