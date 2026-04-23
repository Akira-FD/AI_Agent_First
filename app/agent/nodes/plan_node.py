from __future__ import annotations

from dataclasses import dataclass

from app.agent.nodes.tool_router_node import ToolAction


@dataclass(frozen=True)
class AgentPlan:
    route: str
    should_call_tool: bool = False
    steps: list[str] | None = None


def create_plan(intent: str) -> AgentPlan:
    if intent == "execute":
        return AgentPlan(
            route="tool",
            should_call_tool=True,
            steps=["retrieve_context", "route_tools", "execute_tools", "answer_with_tool_results"],
        )
    if intent == "troubleshoot":
        return AgentPlan(route="diagnose", steps=["retrieve_context", "diagnose_with_context", "answer_with_context"])
    return AgentPlan(route="answer", steps=["retrieve_context", "answer_with_context"])


def create_tool_plan(actions: list[ToolAction]) -> AgentPlan:
    action_steps = [action.tool_name for action in actions]
    return AgentPlan(
        route="tool",
        should_call_tool=True,
        steps=["retrieve_context", *action_steps, "answer_with_tool_results"],
    )


def should_call_tool(intent: str) -> bool:
    return create_plan(intent).should_call_tool
