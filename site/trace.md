# Landing page trace (2026-11-17)

One row per claim in `site/index.html`. The page says nothing the README does not, so each row names its row in [docs/readme-trace.md](../docs/readme-trace.md) and the source under it. A test name is in `tests/`. "Run today" means a command executed in the session that wrote the page, with its output quoted. The four gates ran on a clean copy of commit `179caed` plus the site files.

## Runs in this session

| Command | Output |
|---|---|
| `py -m pip install git+https://github.com/Yasser-Ameur/reach`, typed as on the page, in an empty folder with a new venv active | "Successfully installed ... mcp-2.3.0 ... reach-0.1.0"; `py -m pip show reach`: "Name: reach, Version: 0.1.0" |
| `python -c "from reach import tree, server; print(tree.LIMIT, server.MAX_SIDE)"` | "800 1568" |
| `git show HEAD:src/reach/server.py \| grep -c "@server.tool"` at commit `179caed` | "7" |
| `.venv\Scripts\python.exe -m ruff check .` | "All checks passed!" |
| `.venv\Scripts\python.exe -m ruff format --check .` | "24 files already formatted" |
| `.venv\Scripts\python.exe -m mypy` | "Success: no issues found in 10 source files" |
| `.venv\Scripts\python.exe -m pytest` | "46 passed in 1.00s" |
| read `docs/assets/capture/capture.json` | `elements` 51, `seconds` 0.03, `display` "Text "Die Anzeige lautet 12" [s2e14]" |
| `python scripts/make_site.py` | "copied 6 captures to site/assets" |

Not run again today: the Calculator capture and `claude mcp add`. The capture takes over the mouse. The registration could not be checked to "Connected", because a Reach server was already running in the session and only one runs at a time. Both rest on the README session's runs, quoted in `docs/readme-trace.md`.

The page describes Reach at commit `179caed`, the state the public repository and `docs/readme-trace.md` hold. While the page was written, another change sat uncommitted in the working tree (two more tools, a shared kill switch). None of it is on the page. When it lands with its own trace rows, the tool table, the tool count and the one server limit here need the same update.

## First screen

| Claim on the page | readme-trace row | Source |
|---|---|---|
| "Claude drives a Windows app only after your yes" | The guard: grant by path | `test_read_needs_grant`, `test_tool_read_needs_grant`, `test_grant_keyed_by_path` |
| MCP server, Python, Windows 11 | About box; First screen: `py -m reach` starts the server | `pyproject.toml` dependency `mcp`; README "Windows 11, Python 3.14 or later" |
| Reads one app as a text tree with refs; clicks and types by ref | What Claude sees; Tools | `test_render_gives_refs_and_states`; stdio client listed the seven tools |
| Stops at Ctrl+Alt+Backspace | The guard: kill switch final | `test_tool_refused_after_kill`, `test_kill_stops_input_already_in_flight` |
| `py -m pip install git+https://github.com/Yasser-Ameur/reach` | First screen: same command | run today, above |
| Python 3.14 or later | First screen: Python 3.14 | `pyproject.toml` `requires-python` |
| 51 elements in 0.03 s | What Claude sees: 51 elements | `capture.json`, read today |
| 2 apps driven, nothing else tried | Limits: two apps driven | `scripts/live_check.py` and `scripts/make_hero.py` are the only live runs |
| The Calculator window is real; names are German | First screen: hero is a real run; Windows set to German | `site/assets/frame0.png` is a copy of `docs/assets/capture/frame0.png`; `capture.json` `steps[].line` |
| Tags sit where the snapshot placed those refs | First screen: hero is a real run | `capture.json` `steps[].x`, `steps[].y`, written from the snapshot's own rectangles at `scripts/make_hero.py:102` to `:111` |

## The recorded run

| Claim on the page | readme-trace row | Source |
|---|---|---|
| Dialog, window and every line of text captured; the click on Yes is drawn | First screen: hero is a real run; "The owner said yes" NOT captured | `scripts/make_hero.py:67` to `:74` answers the dialog No; `Guard(..., lambda app: True, ...)` at `:38` grants through the harness |
| Rings, tags and the pointer are marks added on top | none needed: a statement about the page itself | `site/index.html`, the `.ring`, `.tag` and `.ptr` elements |
| The dialog names the executable | The guard: the dialog warns for known shells | `test_allow_dialog_names_the_path_and_warns_for_shells`; `site/assets/dialog.png` |
| No other call runs while a dialog is open | The guard: own windows refused | `test_pending_dialog_blocks_input` |
| Grant stored by executable path in `~/.reach/grants.json` | The guard: grant by path | `test_grant_keyed_by_path`, `test_yes_is_persisted_and_not_asked_again` |
| A yes inside the first second is discarded | The guard: yes inside one second | `test_a_yes_inside_the_first_second_is_not_believed` |
| The four tree lines, the header line and the refs in the calls | First screen: Windows set to German | `capture.json` `header`, `steps[].line`, `steps[].ref` |
| Orange border and label while input is sent; gone once it stops | The guard: overlay appears during input | seen during the live check and the Calculator run, not asserted by a test; label text is `overlay._LABEL` |
| Before a click, Reach checks the app under the point | The guard: app under the point | `test_tool_click_checks_app_under_point` |
| Reach shows whatever names the app exposes | First screen: Windows set to German | `capture.json` |
| Every call is one line in `~/.reach/actions.jsonl` | The guard: every call logged | `test_tool_every_call_logged` |
| A new snapshot reads the display as 12 | First screen: hero is a real run | `capture.json` `display`, read today |
| A ref names its snapshot; old refs match nothing | The guard: old ref matches nothing | `test_tool_old_ref_is_refused` |

## What Claude sees, tools

| Claim on the page | readme-trace row | Source |
|---|---|---|
| The snapshot excerpt | What Claude sees: snapshot excerpt | copied from README; the refs for Plus and Gleich are in `capture.json` |
| `click(ref="s1e35")`; no image tokens, no guessed coordinates | What Claude sees | README text; the tool returns text, `test_render_gives_refs_and_states` |
| `screenshot` returns a PNG of one window; `click` takes its pixels | What Claude sees: screenshot returns a PNG | live check line "click by screenshot pixels landed on the button" |
| Seven tools and their rows | Tools: seven tools; title only for a granted app; 800 elements, 1568 pixels | the count and both constants run today, above; `test_tool_windows_hides_titles_until_granted`, `test_render_truncates_at_the_limit` |

## The guard

Each row on the page links its test at commit `179caed`. The line numbers were read from `tests/` today.

| Row on the page | readme-trace row | Test and line |
|---|---|---|
| The app has no grant | Grant by path; revoke on the next call | `test_reach.py:54`, `test_reach.py:71` |
| You said No | No held until restart | `test_reach.py:63` |
| The yes came too fast | Yes inside one second | `test_server.py:201` |
| The window is Reach's own | Own windows refused; no call during a dialog | `test_reach.py:80`, `test_reach.py:94` |
| The process cannot be inspected; an elevated window was not tried live | Uninspectable process refused | `test_reach.py:87` |
| The input would land elsewhere | App under the point, foreground app | `test_server.py:74`, `test_server.py:87` |
| The keys would act outside the app | Shell and paste combinations | `test_server.py:118` |
| The ref is old | Old ref matches nothing | `test_server.py:106` |
| Focus is in a password field | Password field | `test_server.py:96`, `test_reach.py:180` |
| You pressed Ctrl+Alt+Backspace | Kill switch final, and stops typing in flight | `test_server.py:151` |
| `grants.json`, `actions.jsonl`, and nothing else | Limits: Files section | `guard.Guard.check`, `guard.Guard.log`; the sample lines are the README's examples |

## Limits

| Claim on the page | readme-trace row | Source |
|---|---|---|
| The seven limits, word for word from the README | Limits: menu paste; packaged path; one server at a time. The guard: the dialog warns for known shells | README "What it does not protect against"; `docs/THREAT-MODEL.md` |
| Two apps driven; browsers, Electron, elevated windows, a second monitor not tried | Limits: two apps driven | the two live scripts |

## Run it, footer

| Claim on the page | readme-trace row | Source |
|---|---|---|
| `py -m pip install git+https://github.com/Yasser-Ameur/reach` | First screen | run today, above |
| `claude mcp add reach -- py -m reach` | First screen: "Added stdio MCP server", then "Status: Connected" | README session run, not repeated today |
| The prompt, the dialog, wait a second, Ctrl+Alt+Backspace | The guard | README "Try it" |
| Reach 0.1.0 | First screen: `pip show reach` | `pyproject.toml` `version`; `pip show` today |
| MIT license | First screen: license badge | `LICENSE` |

## Slop pass

The one move no neighbour could copy: the recorded run pinned to the scroll, where the orange border and its kill switch label appear only on the four steps that send input. It is Reach's own overlay, in its own colour, doing on the page what it does on the desktop.

Removed as reflexes: a mask fade under the hero capture (it hid the Gleich ref), a transcript panel repeating the step captions, dimmed inactive steps (they dropped under the contrast floor), a second curve for the pointer, a test count as hero proof (not in the README trace), an "Extend" section (Reach has no SDK), a star badge, a light theme nobody asked for.
