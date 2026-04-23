from __future__ import annotations

from app.agent.nodes.tool_router_node import ToolAction


def build_replan_steps(recovery_action: str, repaired_action: ToolAction | None = None) -> list[str]:
    if recovery_action == "retry_repaired_action" and repaired_action is not None:
        return [recovery_action, repaired_action.tool_name, "answer_with_tool_results"]
    if recovery_action == "retry_later":
        return [recovery_action, "answer_with_retry_guidance"]
    if recovery_action == "degrade_to_answer":
        return [recovery_action, "answer_with_available_context"]
    return []
