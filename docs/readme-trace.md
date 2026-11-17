# README trace (2026-11-17)

One row per claim in README.md. A test name is in `tests/`; "run" means a command executed in the session that wrote the README. Rows marked AFTER PUSH can only be checked once the repository is public and are re-verified then.

## Audit of the first README (commit 042bf90)

| Old claim | Verdict |
|---|---|
| Hero was a snapshot of the test window with refs `e1` | changed: refs carry a generation now, and the hero is a recorded Calculator run |
| "Not published to a package index", install from a checkout | changed: installs from the public repository with pip |
| `.mcp.json` entry pointing at `reach.exe` | changed: `py -m reach`, through `src/reach/__main__.py` |
| "The overlay covers the primary monitor only" | removed: `overlay.py` creates the window over the virtual screen (metrics 76 to 79). Not tried on a second monitor, and the README says so |
| Tool table, guard list | kept, extended |

## First screen

| Claim | Source |
|---|---|
| The hero is a real Calculator run; dialog, window and text captured | `scripts/make_hero.py` run; it wrote `docs/assets/capture/` (five frames, `dialog.png`, `capture.json`) and prints "captured 5 frames, 51 elements in 0.03s: Text "Die Anzeige lautet 12" [s2e14]" |
| "The owner said yes" in the hero | NOT captured: the script answers the real dialog No and grants through its own harness. The README caption says the dialog was captured, not the click |
| Windows set to German; names Sieben, Plus, Fünf, Gleich | `docs/assets/capture/capture.json`, `steps[].line` |
| Hero size | 1000 by 590 units, 388 KB, 13 s, plays once: printed by `make_hero.py`; rendered in a browser and stepped at 2.95 s, 9.25 s and 13 s |
| `py -m pip install git+https://github.com/Yasser-Ameur/reach` | AFTER PUSH |
| `claude mcp add reach -- py -m reach` | Syntax from `claude mcp add --help` run; execution AFTER PUSH |
| `py -m reach` starts the server | `src/reach/__main__.py`; AFTER PUSH from a fresh environment |
| Python 3.14 or later | `pyproject.toml` `requires-python`; every gate ran on 3.14.x, no other version was tried |
| gates badge, license badge | AFTER PUSH |

## What Claude sees

| Claim | Source |
|---|---|
| Snapshot excerpt | Calculator snapshot printed by a probe run this session; the same refs for Plus and Gleich are in `capture.json` |
| 51 elements read in 0.03 s | `capture.json`: `elements`, `seconds` |
| Screenshot returns a PNG of one window; click takes its pixels | live check line "click by screenshot pixels landed on the button" |

## Tools

| Claim | Source |
|---|---|
| Seven tools | stdio client run listed `windows, snapshot, screenshot, click, type_text, press_key, scroll` |
| Title only for a granted app | `server.windows`; NOT asserted by a test |
| 800 elements, 1568 pixels | `tree.LIMIT`, `server.MAX_SIDE`; `test_render_truncates_at_the_limit` for the cap |
| Nothing covering the window appears in a screenshot | `win32.capture` uses PrintWindow; the live check's PNG was opened and showed only the window |

## The guard

| Claim | Source |
|---|---|
| Grant by path, title ignored | `test_grant_keyed_by_path` |
| Revoke on the next call | `test_revoking_a_line_takes_effect_without_restart` |
| No held until restart | `test_denial_cached` |
| Yes inside one second discarded | `win32.ask`; NOT covered by a test, threat model A7 |
| Own windows refused; no call during a dialog | `test_own_process_refused`, `test_pending_dialog_blocks_input` |
| Uninspectable process refused | `test_uninspectable_refused`; an elevated window was NOT tried live |
| App under the point, foreground app | `test_tool_click_checks_app_under_point`, `test_tool_keys_check_foreground`; deleting either check turned that test red in a mutation run |
| Shell and paste combinations | `test_tool_shell_and_paste_combos_refused`; live check line "shell combo: Refused" |
| Old ref matches nothing | `test_tool_old_ref_is_refused`; live check line "stale ref: Refused: s1e2" |
| Password field | `test_tool_password_focus_refuses_keys_and_keeps_text_out_of_log`, `test_password_value_redacted`; live check line "password field: Refused" |
| Kill switch final, and stops typing in flight | live check sent the real hotkey, line "after kill switch: Refused"; `test_kill_stops_input_already_in_flight` |
| Server does not start when the hotkey is taken | run: a second `reach.exe` beside a first exited with code 1 and "Ctrl+Alt+Backspace is taken by another program; Reach will not run" |
| Overlay and its two seconds | `overlay._HOLD_MS`; seen during the live check, not asserted |
| Every call logged | `test_tool_every_call_logged`; live check printed 16 log lines |

## Limits

| Claim | Source |
|---|---|
| Menu paste still works | not tested; threat model A6 |
| Packaged path carries its version | `capture.json` app path seen in the probe: `...microsoft.windowscalculator_11.2607.0.0_x64__8wekyb3d8bbwe\calculatorapp.exe` |
| One server at a time | the two server run above |
| Two apps driven; browsers, Electron, elevated, second monitor not tried | `scripts/live_check.py` and `scripts/make_hero.py` are the only live runs |
| Eight modules | `docs/DESIGN.md`; `src/reach/` holds guard, tree, keys, png, win32, uia, overlay, server |

## Checks

| Claim | Source |
|---|---|
| Gate commands | run on the final tree: ruff clean, mypy clean, pytest green |
| `LIVE CHECK PASSED` | run after the last source change |

## About box

| Field | Source |
|---|---|
| Description | README first sentence without "An" and the full stop |
| Website | empty: no docs site, no demo, no published package |
| `mcp`, `mcp-server`, `model-context-protocol` | `pyproject.toml` dependency `mcp`; `server.py` `MCPServer` |
| `computer-use`, `desktop-automation` | `win32.click`, `send_text`, `send_keys` |
| `claude` | `server._ask` dialog text; README try-it |
| `windows`, `ui-automation` | `uia.py` |
| `python` | `pyproject.toml` |
