from __future__ import annotations

from typing import Any, TypedDict


class AgentState(TypedDict, total=False):
    session_id: str
    user_query: str
    intent: str
    retrieved_docs: list[dict[str, Any]]
    context_text: str
    selected_tool: str
    tool_input: dict[str, Any]
    tool_output: dict[str, Any]
    observations: list[str]
    final_answer: str
    summary: str
    retry_count: int
    error: str
