from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class AgentState:
    session_id: str
    user_query: str
    intent: str = ""
    plan_route: str = ""
    plan_steps: list[str] = field(default_factory=list)
    context_text: str = ""
    sources: list[dict[str, Any]] = field(default_factory=list)
    selected_tool: str = ""
    tool_input: dict[str, Any] = field(default_factory=dict)
    tool_actions: list[dict[str, Any]] = field(default_factory=list)
    tool_output: dict[str, Any] = field(default_factory=dict)
    tool_message: str = ""
    tool_logs: list[dict[str, str]] = field(default_factory=list)
    observations: list[str] = field(default_factory=list)
    recovery_action: str = ""
    replan_steps: list[str] = field(default_factory=list)
    final_answer: str = ""
    summary: str = ""
    answer_backend: str = "unknown"
    provider_status: str = "not_used"
    provider_error: str = ""
    provider_attempts: int = 0
    first_token_latency_ms: int = 0
    total_latency_ms: int = 0
    provider_diagnostic: str = ""
    retrieval_stage_latency_ms: dict[str, int] = field(default_factory=dict)
    node_trace: list[str] = field(default_factory=list)
    retry_count: int = 0
    error: str = ""

    def mark(self, node_name: str) -> None:
        self.node_trace.append(node_name)
