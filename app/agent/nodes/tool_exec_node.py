from __future__ import annotations

from app.tools.registry import ToolRegistry


def execute_tool(tool_name: str, tool_input: dict[str, str], registry: ToolRegistry):
    tool = registry.get(tool_name)
    return tool.run(tool_input)
