# Prior art (audited 2026-11-17)

Five projects were read at source before Reach was called done. Nothing was copied: each idea taken was rewritten here and has a test or a live check behind it. Figures are as read that day.

| Project | What it is | What Reach took | What Reach refused |
|---|---|---|---|
| [openai/codex](https://github.com/openai/codex) | A coding agent. Its tree holds no computer use code: the runtime is a closed bundled plugin. The repository only carries policy around it | Confirmation that a per app allow list is the right unit of permission | A model scoring each action, which needs a hosted model. Grant by publisher and product: Reach keys on the full executable path, which a renamed binary elsewhere does not match |
| [anthropics/claude-quickstarts](https://github.com/anthropics/claude-quickstarts), `computer-use-demo` | Anthropic's reference computer tool, driven by screenshots of a whole screen | Drag, hover, clicks with held keys, with every key and button released in a `finally`. A bounds check on coordinates. Limits on one call | A fixed two second sleep after every action. Whole screen scope with no per app grant. Shell strings |
| [microsoft/playwright-mcp](https://github.com/microsoft/playwright-mcp) | Browser automation from an accessibility snapshot with refs | An action can return the new tree in the same call. A short wait before reporting. Search within a snapshot. Read only annotations on the reading tools | Running arbitrary code in the page. Raw selectors beside refs. Its refs restart at `e1` on each snapshot; Reach's carry a generation |
| [CursorTouch/Windows-MCP](https://github.com/CursorTouch/Windows-MCP) | A Windows desktop MCP server on UI Automation | Timeouts on the UI Automation client, so a hung app costs one failed call. A cap on tree depth. A truncation message that names the remedy | PowerShell, registry, file and process tools with no grant. Telemetry on by default. Global input hooks |
| [mediar-ai/terminator](https://github.com/mediar-ai/terminator) | A desktop automation library with an MCP server | Checks before a click: the element must be enabled, in view, have an area and lie inside its window | A shell tool and file tools. Telemetry on by default. Acting through UI Automation patterns with no pointer movement, which the owner could not see |

## Left for later, on purpose

- Scrolling a named element into view. Reach refuses a click on an element out of view and tells the model to scroll; it does not scroll for it.
- Zooming into part of a screenshot at full resolution.
- Web content in Firefox, which needs a second accessibility interface.
- Taking control back when the owner moves the mouse. The kill switch is the one way to stop a run.
- A grant that lasts one run only.
