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
    children: list["Node"] = field(default_factory=list)


def _clip(text: str, limit: int) -> str:
    text = " ".join(text.split())
    return text if len(text) <= limit else text[: limit - 1] + "…"


def render(root: Node, generation: int, limit: int = LIMIT) -> tuple[str, dict[str, Rect]]:
    """One line per on-screen element. Returns the text and the rect behind each ref.

    A ref carries the snapshot's generation (`s3e12`), so a ref remembered from an
    older snapshot matches nothing in a newer one and cannot hit another element."""
    lines: list[str] = []
    refs: dict[str, Rect] = {}

    def walk(node: Node, depth: int) -> bool:
        if node.offscreen:
            return True
        # An empty text field is a target; an empty nameless pane is noise.
        if node.name or node.value or node.children or node.role not in _FILLER:
            if len(refs) >= limit:
                lines.append(f"... truncated at {limit} elements")
                return False
            ref = f"s{generation}e{len(refs) + 1}"
            refs[ref] = node.rect
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
            lines.append(line)
        return all(walk(child, depth + 1) for child in node.children)

    walk(root, 0)
    return "\n".join(lines), refs
