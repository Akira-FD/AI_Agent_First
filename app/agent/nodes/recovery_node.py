from __future__ import annotations

from app.models.tool_result import ToolResult
from app.agent.nodes.tool_router_node import ToolAction


def choose_recovery_action(result: ToolResult) -> str:
    if result.success:
        return "none"
    if build_repaired_action("", result) is not None:
        return "retry_repaired_action"
    if result.retryable:
        return "retry_later"
    return "degrade_to_answer"


def build_repaired_action(tool_name: str, result: ToolResult) -> ToolAction | None:
    if not result.retryable or not isinstance(result.data, dict):
        return None
    repaired_payload = result.data.get("repaired_payload")
    if not isinstance(repaired_payload, dict):
        return None
    return ToolAction(tool_name=tool_name, tool_input={str(key): str(value) for key, value in repaired_payload.items()})
