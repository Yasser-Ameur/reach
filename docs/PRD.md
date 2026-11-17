# Reach

Reach lets a developer hand Claude one Windows app at a time: Claude reads the app as a tree of named elements, acts on it with mouse and keyboard, and cannot touch anything the developer has not allowed at the keyboard.

## 1. Problem

An MCP client gives Claude a shell and often a browser. A native Windows app, such as a settings pane, an installer, an IDE dialog or a game editor, is out of reach from there. Computer use driven by screenshots costs image tokens on every step and makes the model guess pixel coordinates, and it is rarely scoped to one app.

Evidence is thin and stated as such: this is one developer's own need, seen in this workspace where Roblox Studio, the Android emulator and Comfy Desktop each needed a hand-written bridge. No interviews were run.

## 2. Who it is for

A developer on Windows 11 who already runs Claude through an MCP client and wants it to finish a task inside a desktop app while they watch. The job: "do the clicking in this one app for me, and do not wander."

## 3. Appetite and no-gos

Appetite: one build session for a working guarded server, with a README.

No-gos:

- No agent loop and no API key. The MCP client is the agent.
- No launching processes and no shell. Opening an app goes through an already granted app or the owner.
- No macOS or Linux.
- No driving elevated windows, UAC prompts or the lock screen.
- No typing into password fields, even on request.
- No remote transport. stdio only.
- No recording, replay or macro format.

## 4. Requirements

Testing seam: the guard, the tree renderer, the key parser and the PNG encoder are pure Python and are tested directly. The Win32 and UI Automation calls sit behind them and are exercised by one live check against Notepad (`scripts/live_check.py`).

Perception

- R1. `windows` MUST list every visible top level window with its app name and whether the app holds a grant, and MUST show the title only for a granted app.
- R2. `snapshot` MUST return the UI Automation tree of one window as text, one on-screen element per line with a ref, role, name and state, and MUST cap output at 800 elements with a stated truncation line.
- R3. `snapshot` MUST replace the value of any password element with `[redacted]`.
- R4. `screenshot` MUST return a PNG of one window whose long side is at most 1568 pixels, captured from the window itself so the overlay and other windows never appear in it.

Action

- R5. `click` MUST accept either a ref from the latest snapshot or x and y in the latest screenshot's pixels, and MUST refuse a ref from an older snapshot. A ref carries its snapshot's generation, as in `s3e12`.
- R6. `type_text` MUST send Unicode text to the granted foreground window, and `press_key` MUST send one combination such as `ctrl+s`, and MUST refuse the Windows key, task switching combinations and paste.
- R7. `scroll` MUST scroll at a ref or a point by a signed number of wheel notches.

Guard

- R8. Every tool that reads or acts on a window MUST refuse unless that window's app holds a grant. The default with no grants file is refusal.
- R9. The first call against an app with no grant MUST raise one native allow dialog naming the executable path. A no MUST be remembered until restart, so one app raises at most one dialog per server run.
- R10. Reach MUST refuse to act on its own windows, so the model can never answer the allow dialog.
- R11. Reach MUST refuse an app whose process it cannot inspect, which covers elevated processes.
- R12. Before any click or scroll, Reach MUST check the app under the target point, and before any keystroke the app holding the foreground. A mismatch with the named window is a refusal.
- R13. `type_text` and `press_key` MUST refuse while keyboard focus is in a password element.
- R14. Ctrl+Alt+Backspace MUST make every later tool call fail until the server restarts. If the hotkey cannot be registered the server MUST NOT start.
- R15. Every tool call, allowed or refused, MUST append one JSON line to `~/.reach/actions.jsonl`.
- R16. During input Reach SHOULD show a click-through overlay naming the kill switch, hidden two seconds after the last action.

## 5. Success metrics

Measured by hand; there is no telemetry.

- Goal: on the live check, Claude completes "type a line in Notepad and save it" using snapshots only, with zero screenshots.
- Counter-metric: actions delivered to an app with no grant. Must be 0. One is a release blocker.
- Guardrail: a snapshot of a typical window stays under 800 lines and returns in under 2 seconds.

## 6. Experience

No screen of its own beyond the allow dialog and the overlay.

- Refused call: the tool returns an error starting with `Refused:` and the reason, so the model can tell the owner what to do.
- Stale ref: `Refused: e12 is not in the latest snapshot of this window. Take a new snapshot.`
- App with no usable tree: the snapshot is short; the model falls back to `screenshot` and x, y.

## 7. Dependencies and open questions

Dependencies: Python 3.13 or later, the `mcp` package, `comtypes`.

Riskiest assumption: UI Automation trees of real apps are rich enough that refs carry most actions. Tested first by the live check on Notepad; wider apps are open.

- Open: how good are the trees of Chromium and Electron apps without a screen reader flag? Owner Yasser, by 2026-12-01.
- Open: should a grant expire? Owner Yasser, by 2026-12-01.

## 8. Rollout

Local git only. Registered in one MCP client by hand (see README). Off switch: remove the server from the client config, or press the kill switch. Public repository after the README and a recorded demo exist.

## 9. Non-goals and known weaknesses

- Screen content can carry instructions aimed at the model. Reach limits the blast radius with grants; it does not detect injection.
- A grant on a terminal, a file manager or a browser is close to a grant on the whole account. The allow dialog says so for known shells, and the owner decides.
- The check in R12 and the input that follows are two steps. A window that takes focus in between receives the input. Accepted, see the threat model.
- Typed text is written to the action log in clear.
