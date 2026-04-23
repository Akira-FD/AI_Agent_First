from __future__ import annotations

from app.models.tool_result import ToolResult


def observe_tool_result(result: ToolResult) -> list[str]:
    status = "success" if result.success else "failed"
    return [f"tool_result:{status}:{result.code}:{result.message}"]
