from __future__ import annotations

from app.models.tool_result import ToolResult
from app.agent.nodes.tool_router_node import ToolAction


def choose_replan_action(
    failed_action: ToolAction,
    recovery_action: str,
    remaining_actions: list[ToolAction],
    result: ToolResult,
) -> str:
    if recovery_action == "degrade_to_answer" and failed_action.tool_name == "check_service_status":
        if "查看错误日志" in result.message and any(action.tool_name == "search_error_logs" for action in remaining_actions):
            return "fallback_to_remaining_actions"
    return recovery_action


def build_replan_steps(recovery_action: str, repaired_action: ToolAction | None = None) -> list[str]:
    if recovery_action == "retry_repaired_action" and repaired_action is not None:
        return [recovery_action, repaired_action.tool_name, "answer_with_tool_results"]
    if recovery_action == "fallback_to_remaining_actions" and repaired_action is not None:
        return [recovery_action, repaired_action.tool_name, "answer_with_tool_results"]
    if recovery_action == "retry_later":
        return [recovery_action, "answer_with_retry_guidance"]
    if recovery_action == "degrade_to_answer":
        return [recovery_action, "answer_with_available_context"]
    return []
