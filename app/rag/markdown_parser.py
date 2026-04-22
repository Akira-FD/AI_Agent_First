from __future__ import annotations

import re
from dataclasses import dataclass, field


@dataclass
class MarkdownSection:
    title: str
    level: int
    path: list[str] = field(default_factory=list)
    content: list[str] = field(default_factory=list)

    @property
    def text(self) -> str:
        return "\n".join(line for line in self.content if line is not None).strip()


class MarkdownParser:
    heading_pattern = re.compile(r"^(#{1,6})\s+(.+)$")

    def parse(self, text: str) -> list[MarkdownSection]:
        sections: list[MarkdownSection] = []
        path_stack: list[str] = []
        current = MarkdownSection(title="ROOT", level=0, path=[])

        for line in text.splitlines():
            match = self.heading_pattern.match(line)
            if match:
                if current.text:
                    sections.append(current)
                level = len(match.group(1))
                title = match.group(2).strip()
                path_stack = path_stack[: level - 1]
                path_stack.append(title)
                current = MarkdownSection(title=title, level=level, path=list(path_stack))
            else:
                current.content.append(line)

        if current.text:
            sections.append(current)
        return sections
