# README trace (2026-11-17)

One row per claim in README.md. A test name is in `tests/`; "run" means a command executed in the session that wrote the README. Rows that depend on the public repository were run after the first push.

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
| The animation plays on GitHub | the repository page was opened in a browser after the push and the hero was seen mid run |
| The hero is a real Calculator run; dialog, window and text captured | `scripts/make_hero.py` run; it wrote `docs/assets/capture/` (five frames, `dialog.png`, `capture.json`) and prints "captured 5 frames, 51 elements in 0.03s: Text "Die Anzeige lautet 12" [s2e14]" |
| "The owner said yes" in the hero | NOT captured: the script answers the real dialog No and grants through its own harness. The README caption says the click on Yes is drawn |
| Windows set to German; names Sieben, Plus, Fünf, Gleich | `docs/assets/capture/capture.json`, `steps[].line` |
| Hero size | 1000 by 590 units, 388 KB, 13 s, plays once: printed by `make_hero.py`; rendered in a browser and stepped at 2.95 s, 9.25 s and 13 s |
| `py -m pip install git+https://github.com/Yasser-Ameur/reach` | run after the push in a clean venv: `pip show reach` gave "Version: 0.1.0, Requires: comtypes, mcp" |
| `claude mcp add reach -- py -m reach` | run after the push in a scratch folder, with the clean venv's python in place of `py`: "Added stdio MCP server", then `claude mcp get` reported "Status: Connected"; removed afterwards |
| `py -m reach` starts the server | run after the push: an MCP client started `python -m reach` from the clean venv and listed the seven tools |
| Python 3.14 or later | `pyproject.toml` `requires-python`; every gate ran on 3.14.x, no other version was tried |
| gates badge, license badge | both URLs returned 200; `gh run list` showed the gates run on main "completed success"; the rendered page showed "gates passing" and "license MIT" |

## What Claude sees

| Claim | Source |
|---|---|
| Snapshot excerpt | Calculator snapshot printed by a probe run this session; the same refs for Plus and Gleich are in `capture.json` |
| 51 elements read in 0.03 s | `capture.json`: `elements`, `seconds` |
| Screenshot returns a PNG of one window; click takes its pixels | live check line "click by screenshot pixels landed on the button" |

## Tools

| Claim | Source |
|---|---|
| Nine tools, three marked read only | `test_reads_are_marked_read_only` lists them through the server |
| `find` keeps matches with ancestors, out of view included, never a password value | `test_find_keeps_matches_with_their_ancestors_and_reaches_out_of_view`, `test_find_never_matches_a_password_value`; live check line "find kept only the match, and hover reached it" |
| Click with keys held, hover, drag | `test_tool_click_holds_modifiers_and_logs_the_element`, `test_tool_hover_and_drag_check_every_point`; live check lines "drag selected the text" and "shift+click extended the selection" |
| `then_snapshot` returns the new tree, after a short wait | `test_tool_action_can_return_the_new_tree`; `server.SETTLE`; live check line "the action returned the new tree" |
| Title only for a granted app | `test_tool_windows_hides_titles_until_granted` |
| 800 elements, 1568 pixels | `tree.LIMIT`, `server.MAX_SIDE`; `test_render_truncates_at_the_limit` for the cap |

## The guard

| Claim | Source |
|---|---|
| Grant by path, title ignored | `test_grant_keyed_by_path` |
| Revoke on the next call | `test_revoking_a_line_takes_effect_without_restart` |
| No held until restart | `test_denial_cached` |
| Yes inside one second discarded | `test_a_yes_inside_the_first_second_is_not_believed` |
| The dialog warns for known shells | `test_allow_dialog_names_the_path_and_warns_for_shells` |
| Own windows refused; no call during a dialog | `test_own_process_refused`, `test_pending_dialog_blocks_input` |
| Uninspectable process refused | `test_uninspectable_refused`; an elevated window was NOT tried live |
| App under the point, foreground app | `test_tool_click_checks_app_under_point`, `test_tool_keys_check_foreground`; deleting either check turned that test red in a mutation run |
| Shell and paste combinations | `test_tool_shell_and_paste_combos_refused`; live check line "shell combo: Refused" |
| A target that cannot be acted on is refused | `test_tool_never_clicks_what_cannot_be_clicked`, `test_tool_point_must_be_inside_the_screenshot_and_the_window` |
| Old ref matches nothing | `test_tool_old_ref_is_refused`; live check line "stale ref: Refused: s1e2" |
| Password field | `test_tool_password_focus_refuses_keys_and_keeps_text_out_of_log`, `test_password_value_redacted`; live check line "password field: Refused" |
| Kill switch final, and stops typing in flight | live check sent the real hotkey, line "after kill switch: Refused"; `test_kill_stops_input_already_in_flight` |
| A held key or button is released first | `test_held_keys_come_back_up_even_when_the_click_fails`, `test_drag_lets_go_of_the_button_when_killed_midway` |
| One press stops every Reach server; a non Reach holder blocks startup | `scripts/kill_switch_check.py` run: "two servers run side by side", "one press stopped both", "the survivor took the hotkey over and stopped", "a server started after the press runs", "a server refuses to start when the hotkey is not Reach's" |
| Overlay appears during input and goes away after | seen during the live check and the Calculator run; not asserted by a test |
| Every call logged | `test_tool_every_call_logged`; live check printed 23 log lines |

## Limits

| Claim | Source |
|---|---|
| Menu paste is not blocked | no code path inspects menus; `keys.parse` refuses only the key combinations |
| Files section: list of paths, one JSON line per call, key order | `guard.Guard.check` and `guard.Guard.log`; `test_tool_every_call_logged` reads the lines back. The two sample lines are examples, with real key order and a real refusal message |
| Refusal messages in the table | each string is raised in `guard.py`, `keys.py`, `server.py` or `win32.py`; matched by the `match=` patterns in `tests/` |
| Packaged path carries its version | `capture.json` app path seen in the probe: `...microsoft.windowscalculator_11.2607.0.0_x64__8wekyb3d8bbwe\calculatorapp.exe` |
| Other projects were read at source | `docs/PRIOR-ART.md`; five audit reports written the same day, each citing file and line in a clone |
| Two apps driven; browsers, Electron, elevated, second monitor not tried | `scripts/live_check.py` and `scripts/make_hero.py` are the only live runs |
| Eight modules | `docs/DESIGN.md`; `src/reach/` holds guard, tree, keys, png, win32, uia, overlay, server |

## Checks

| Claim | Source |
|---|---|
| Gate commands | run on the final tree: ruff clean, mypy clean, pytest green |
| `LIVE CHECK PASSED` | run after the last source change, on its own kill key Ctrl+Alt+F12 |

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
