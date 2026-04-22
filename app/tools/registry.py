from __future__ import annotations

from app.tools.ops_tools import (
    CheckServiceStatusTool,
    GetIncidentSummaryTool,
    RestartMockServiceTool,
    SearchErrorLogsTool,
)


class ToolRegistry:
    def __init__(self) -> None:
        self._tools: dict[str, object] = {}

    @classmethod
    def with_defaults(cls) -> "ToolRegistry":
        registry = cls()
        for tool in (
            CheckServiceStatusTool(),
            SearchErrorLogsTool(),
            RestartMockServiceTool(),
            GetIncidentSummaryTool(),
        ):
            registry.register(tool.definition.name, tool)
        return registry

    def register(self, name: str, tool: object) -> None:
        self._tools[name] = tool

    def get(self, name: str):
        return self._tools[name]
