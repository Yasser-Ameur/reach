# Reach visual identity

How Reach looks on every surface. The architecture is in [docs/DESIGN.md](docs/DESIGN.md).

Reach is read by a developer deciding whether to let a model touch their desktop. They are wary, and they want to see the limits before the features. The mechanism is one sentence: a window becomes text with refs, and nothing is read or clicked before a yes at the keyboard. The pair is watchful and exact. The distinctive move is that the brand colour is not chosen: it is the orange of the border Reach draws on screen while it sends input, `overlay._ORANGE`. On every surface orange means the same thing it means on the desktop: Reach is acting here, or this is a ref it can act on.

## Not this

- No headline that is the product name plus a definition, the form four of five neighbours use (Windows-MCP, Playwright MCP, UI-TARS Desktop, the computer use tool page). The headline is a promise a reader can check.
- No star count, download badge or unsourced benchmark as proof (Windows-MCP, UI-TARS Desktop, Terminator). Proof is the recorded run and the test behind each refusal.
- No "entire desktop" or "any application" (Terminator). Reach names one app at a time and says which two it has driven.
- No drawn interface. Every window on a Reach surface is a capture from `scripts/make_hero.py`.

## Colour

One theme. The ground is the dark the recorded run was captured on, and the README hero already uses it.

```css
:root {
  --ground: #0d1117;  --surface: #11161d;  --surface-2: #161c25;  --desk: #1a2330;
  --line: #232b36;
  --ink: #e8edf3;  --ink-2: #a6b0bc;  --ink-3: #8791a0;
  --accent: #E06C20;  --accent-ink: #0d1117;  --accent-rgb: 224,108,32;
  --overlay-ink: #ffffff;
}
```

| Pair | Ratio | Floor |
|---|---|---|
| --ink on --ground, --surface | 16.08, 15.43 | 4.5 |
| --ink-2 on --ground, --surface, --surface-2 | 8.61, 8.27, 7.79 | 4.5 |
| --ink-3 on --ground, --surface, --surface-2, --desk | 5.94, 5.70, 5.37, 4.96 | 4.5 |
| --accent on --ground, --surface, --surface-2 | 5.71, 5.48, 5.16 | 4.5 |
| --accent-ink on --accent | 5.71 | 4.5 |
| --overlay-ink on --accent | 3.31 | 3, large text only |

Measured with `contrast.py` on 2026-11-17. `--overlay-ink` on `--accent` is the overlay label as `overlay.py` paints it. It is used only where the overlay itself is shown, at 19 px bold or larger. Page copy on orange uses `--accent-ink`. The only shadow is black at 50 percent under things that float.

Siblings in the workspace sit on amber, gold, green, petrol, indigo, plum and vermilion. Reach's orange is 18 degrees from the nearest, FlowOS amber. It stays because it is the product's own pixel, not a pick.

`docs/assets/hero.svg` was built before this file. Its note lines use `#77828f` where the page uses `--ink-3`; the next rebuild of the hero takes the token.

## Type

No font is fetched. Reach's only interface is a Windows dialog and a label painted by the shell, so the page wears the faces Windows ships.

| Role | Stack | Size | Weight | Tracking |
|---|---|---|---|---|
| Display | "Segoe UI Variable Display", "Segoe UI", system-ui, -apple-system, sans-serif | clamp(2.4rem, 5.4vw, 3.75rem), line 1.05 | 600 | -0.022em |
| Section title | same | clamp(1.75rem, 3.2vw, 2.5rem), line 1.12 | 600 | -0.018em |
| Body | "Segoe UI Variable Text", "Segoe UI", system-ui, -apple-system, sans-serif | 1.0625rem, line 1.6 | 400 | 0 |
| Mono | "Cascadia Mono", "Cascadia Code", Consolas, ui-monospace, SFMono-Regular, Menlo, monospace | 0.84rem, line 1.65 | 400 | 0 |

The mono carries everything Reach itself produces: tool calls, tree lines, refs, file paths, refusal messages, test names. Prose never uses it.

## Shape and space

| Thing | Radius |
|---|---|
| Panels, captures, the desk | 10 px |
| Buttons, code chips, ref tags | 6 px |

Spacing steps: 4, 8, 12, 16, 24, 32, 48, 72, 112 px. Hairlines are 1 px `--line`. A shadow goes only under a thing that floats over a capture.

```css
:root { --container-max: 1120px; --gutter: 24px; --section-y: 112px; --focus-ring: 2px solid var(--accent); }
```

Under 860 px the gutter is 16 px and `--section-y` is 72 px.

## Motif and mark

Two motifs, both from the mechanism. The ref: an identifier such as `[s1e35]` set in mono and orange, wherever an element is named. The hold border: a 4 px orange outline with the kill switch label, drawn only around a depiction of the desktop while input is being sent, and never as decoration.

The mark is the hold border in miniature, an orange outline square on the ground: `site/assets/mark.svg`, drawn by hand. It is the favicon and sits before the wordmark. The wordmark is "Reach" in the display face.

## Motion

One curve, `cubic-bezier(.25,.46,.45,.94)`, the one the README hero uses. Only `transform` and `opacity` move.

| Move | Duration |
|---|---|
| Hover, press, colour | 140 ms |
| Pointer travel in the recorded run | 380 ms |
| A frame, the dialog or the border entering, leaving | 200 ms, 80 ms |
| Click ring | 450 ms, once |
| Entrance, reveal | 600 ms, 560 ms, 65 ms stagger |

The one moment that may be noticed is the recorded run: pinned while its eight steps scroll past, the pointer travelling to each ref. Nothing plays by itself for longer than two seconds, and nothing loops.

Under `prefers-reduced-motion`, or with the page's own motion switch off, the run is unpinned and each step shows its own capture in normal flow. Translate and scale are dropped and durations collapse to 0.01 s. With JavaScript off the page reads the same way.

## Voice

1. Say what Reach refuses before what it does.
2. Say what was tried and what was not. A number comes with the run it came from.
3. Use the glossary words in `CONTEXT.md`: app, grant, snapshot, ref, guard, hold, kill switch.

On voice: "Reach has driven two apps." Off voice: "Control your entire desktop with one prompt."

## Surfaces

- `site/index.html` reads the colour, type, shape and motion blocks.
- `docs/assets/hero.svg`, built by `scripts/make_hero.py`, uses the ground, the surface, the line and the accent.
- `site/assets/` holds the captures, copied from `docs/assets/capture/` by `scripts/make_site.py`.
