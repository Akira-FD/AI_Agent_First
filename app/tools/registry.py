from __future__ import annotations

from app.tools.ops_tools import (
    CheckServiceStatusTool,
    ControlledToolRuntime,
    GetIncidentSummaryTool,
    RestartMockServiceTool,
    SearchErrorLogsTool,
)


class ToolRegistry:
    def __init__(self) -> None:
        self._tools: dict[str, object] = {}

    @classmethod
    def with_defaults(cls, settings=None, command_runner=None) -> "ToolRegistry":
        registry = cls()
        runtime = ControlledToolRuntime.from_settings(settings, command_runner=command_runner) if settings is not None else None
        for tool in (
            CheckServiceStatusTool(runtime=runtime),
            SearchErrorLogsTool(runtime=runtime),
            RestartMockServiceTool(runtime=runtime),
            GetIncidentSummaryTool(),
        ):
            registry.register(tool.definition.name, tool)
        return registry

    def register(self, name: str, tool: object) -> None:
        self._tools[name] = tool

    def get(self, name: str):
        return self._tools[name]
