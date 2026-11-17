# Reach glossary

## App
One program on the desktop, as the guard sees it.
Not: a window. One app may own many windows, and a window title is never part of the identity.
Identified by: the full path of its executable, lower case.
Relates to: zero or one Grant.

## Grant
The owner's recorded yes that Claude may read and drive one App.
Not: a permission the model can request for itself in text. Only the allow dialog creates one.
Identified by: the App's executable path in `~/.reach/grants.json`.
Relates to: exactly one App. Removing the line revokes it.

## Allow dialog
The native Windows prompt Reach raises the first time a tool call touches an App with no Grant.
Not: reachable by Reach's own input tools. Reach never acts on its own windows.
Relates to: a yes writes a Grant; a no is remembered until the server restarts.

## Snapshot
A text rendering of one window's UI Automation tree, one element per line, each with a Ref.
Not: a screenshot, which is pixels and carries no Refs.
Relates to: one window; it replaces every earlier Ref for that window.

## Ref
A short handle such as `s3e12` naming one element in the latest Snapshot of a window: snapshot generation 3, element 12.
Not: stable. A new Snapshot of the same window invalidates the old Refs.
Identified by: the window handle plus the Ref string.

## Guard
The single check every tool call passes before it reads or acts.
Refuses when: the kill switch has fired, the App has no Grant, the App is Reach itself, the App runs elevated, or keyboard focus sits in a password field.

## Hold
The span during which Reach is sending input, shown by the Overlay.
Starts at an input action and ends two seconds after the last one.

## Overlay
The click-through border and label drawn on screen during a Hold.
Not: part of any screenshot Reach returns.

## Kill switch
The global hotkey Ctrl+Alt+Backspace. Once pressed, every tool call is refused until the server restarts.
Not: a pause. There is no resume.

## Action log
The append-only file `~/.reach/actions.jsonl`, one line per tool call, allowed or refused.
