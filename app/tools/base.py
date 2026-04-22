from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from app.models.tool_result import ToolResult


@dataclass
class ToolDefinition:
    name: str
    description: str


class Tool(Protocol):
    definition: ToolDefinition

    def run(self, payload: dict[str, str]) -> ToolResult:
        ...
