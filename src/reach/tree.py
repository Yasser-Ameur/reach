"""Element tree to text with refs. Pure Python."""

from dataclasses import dataclass, field

Rect = tuple[int, int, int, int]  # left, top, right, bottom in screen pixels

LIMIT = 800
_NAME_MAX = 80
_VALUE_MAX = 200
_FILLER = frozenset({"Custom", "Group", "Image", "Pane", "Separator", "Text"})


@dataclass
class Node:
    role: str
    name: str = ""
    value: str = ""
    rect: Rect = (0, 0, 0, 0)
    enabled: bool = True
    focused: bool = False
    password: bool = False
    offscreen: bool = False
    children: list[Node] = field(default_factory=list)

    @property
    def label(self) -> str:
        """How the element reads in a log line or an error: `Button "Save"`."""
        return f'{self.role} "{_clip(self.name, _NAME_MAX)}"' if self.name else self.role


def _clip(text: str, limit: int) -> str:
    text = " ".join(text.split())
    return text if len(text) <= limit else text[: limit - 1] + "…"


def render(
    root: Node, generation: int, limit: int = LIMIT, find: str | None = None
) -> tuple[str, dict[str, Node]]:
    """One line per element. Returns the text and the element behind each ref.

    A ref carries the snapshot's generation (`s3e12`), so a ref remembered from an
    older snapshot matches nothing in a newer one and cannot hit another element.

    Without `find`, elements scrolled out of view are left out. With `find`, only
    elements whose name or value contains it are kept, each with its ancestors, and
    those out of view are kept too and marked, so a search reaches past the limit."""
    lines: list[str] = []
    refs: dict[str, Node] = {}
    needle = find.casefold() if find else None
    on_path: set[int] = set()  # ids of the nodes that lead to a match

    def mark(node: Node) -> bool:
        assert needle is not None
        hit = needle in node.name.casefold()
        hit = hit or (not node.password and needle in node.value.casefold())
        for child in node.children:  # every child, not only up to the first hit
            hit = mark(child) or hit
        if hit:
            on_path.add(id(node))
        return hit

    def walk(node: Node, depth: int) -> bool:
        if needle is None and node.offscreen:
            return True
        if needle is not None and id(node) not in on_path:
            return True
        # An empty text field is a target; an empty nameless pane is noise.
        if node.name or node.value or node.children or node.role not in _FILLER:
            if len(refs) >= limit:
                lines.append(
                    f"... truncated at {limit} elements. "
                    "Call snapshot with find= to search the rest."
                )
                return False
            ref = f"s{generation}e{len(refs) + 1}"
            refs[ref] = node
            line = f"{'  ' * depth}{node.role}"
            if node.name:
                line += f' "{_clip(node.name, _NAME_MAX)}"'
            line += f" [{ref}]"
            if node.password:
                line += " value=[redacted]"
            elif node.value:
                line += f' value="{_clip(node.value, _VALUE_MAX)}"'
            if not node.enabled:
                line += " (disabled)"
            if node.focused:
                line += " (focused)"
            if node.offscreen:
                line += " (out of view)"
            lines.append(line)
        return all(walk(child, depth + 1) for child in node.children)

    if needle is not None:
        mark(root)
    walk(root, 0)
    return "\n".join(lines), refs
