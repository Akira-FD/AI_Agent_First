from __future__ import annotations

from dataclasses import asdict
from dataclasses import dataclass, field

from langgraph.graph import END, START, StateGraph

from app.agent.nodes.answer_node import build_answer
from app.agent.nodes.intent_node import detect_intent
from app.agent.nodes.observation_node import observe_tool_result
from app.agent.nodes.plan_node import create_plan, create_tool_plan
from app.agent.nodes.replan_node import build_replan_steps, choose_replan_action
from app.agent.nodes.recovery_node import build_repaired_action, choose_recovery_action
from app.agent.nodes.retrieve_node import run_retrieval
from app.agent.nodes.summary_node import update_summary
from app.agent.nodes.tool_exec_node import execute_tool
from app.agent.nodes.tool_router_node import ToolAction, route_tools
from app.agent.state import AgentState
from app.rag.retriever import Retriever
from app.services.summary_service import SummaryService


@dataclass
class AgentResponse:
    intent: str
    answer: str
    sources: list[dict[str, str]] = field(default_factory=list)
    tool_logs: list[dict[str, str]] = field(default_factory=list)
    summary: str = ""
    answer_backend: str = "unknown"
    provider_status: str = "not_used"
    provider_error: str = ""
    provider_attempts: int = 0
    first_token_latency_ms: int = 0
    total_latency_ms: int = 0
    provider_diagnostic: str = ""
    retrieval_stage_latency_ms: dict[str, int] = field(default_factory=dict)
    retrieval_backend: str = "unknown"
    embedding_backend: str = "unknown"
    reranker_backend: str = "unknown"
    node_trace: list[str] = field(default_factory=list)
    selected_tool: str = ""
    plan_route: str = ""
    plan_steps: list[str] = field(default_factory=list)
    observations: list[str] = field(default_factory=list)
    recovery_action: str = ""
    replan_steps: list[str] = field(default_factory=list)
    tool_actions: list[dict[str, object]] = field(default_factory=list)


class MVPAgent:
    def __init__(
        self,
        settings,
        repository,
        session_service,
        document_service,
        llm_service,
        tool_registry,
        retriever=None,
        vector_store=None,
    ) -> None:
        self.settings = settings
        self.repository = repository
        self.session_service = session_service
        self.document_service = document_service
        self.llm_service = llm_service
        self.tool_registry = tool_registry
        self.retriever = retriever or Retriever(
            repository=repository,
            top_k=settings.retrieval_top_k,
            vector_store=vector_store,
        )
        self.summary_service = SummaryService(session_service)
        self._graph = self._build_graph()
        self._compiled_graph = self._graph.compile()

    def run(self, session_id: str, user_query: str, tool_actions: list[ToolAction] | None = None) -> AgentResponse:
        state = self._invoke_graph(session_id=session_id, user_query=user_query, tool_actions=tool_actions)
        answer_result = build_answer(
            llm_service=self.llm_service,
            user_query=user_query,
            context_text=state.answer_context_text,
            tool_message=state.tool_message or None,
        )
        return self._finalize_state(
            session_id=session_id,
            user_query=user_query,
            state=state,
            answer_result=answer_result,
        )

    def stream(self, session_id: str, user_query: str, tool_actions: list[ToolAction] | None = None):
        state = self._invoke_graph(session_id=session_id, user_query=user_query, tool_actions=tool_actions)
        final_result = None
        backend_label = ""
        if hasattr(self.llm_service, "backend_label"):
            backend_label = str(self.llm_service.backend_label())
        if hasattr(self.llm_service, "stream_answer_result") and backend_label.startswith("openai-compatible:"):
            for event in self.llm_service.stream_answer_result(
                user_query=user_query,
                context_text=state.answer_context_text,
                tool_message=state.tool_message or None,
            ):
                if event.type == "delta":
                    yield {"type": "delta", "delta": event.delta}
                elif event.type == "done":
                    final_result = event.result
                    break
        if final_result is None:
            final_result = build_answer(
                llm_service=self.llm_service,
                user_query=user_query,
                context_text=state.answer_context_text,
                tool_message=state.tool_message or None,
            )
        response = self._finalize_state(
            session_id=session_id,
            user_query=user_query,
            state=state,
            answer_result=final_result,
        )
        yield {"type": "done", "response": response}

    def _invoke_graph(self, *, session_id: str, user_query: str, tool_actions: list[ToolAction] | None) -> AgentState:
        initial_state = AgentState(session_id=session_id, user_query=user_query)
        if tool_actions:
            initial_state.pending_tool_actions = [
                {"tool_name": action.tool_name, "tool_input": dict(action.tool_input)}
                for action in tool_actions
            ]
        final_state = self._compiled_graph.invoke(initial_state)
        if isinstance(final_state, AgentState):
            return final_state
        if isinstance(final_state, dict):
            return AgentState(**final_state)
        raise TypeError(f"Unsupported graph state: {type(final_state)!r}")

    def _build_graph(self):
        graph = StateGraph(AgentState)
        graph.add_node("load_memory", self._node_load_memory)
        graph.add_node("persist_user_message", self._node_persist_user_message)
        graph.add_node("intent", self._node_intent)
        graph.add_node("retrieve", self._node_retrieve)
        graph.add_node("plan", self._node_plan)
        graph.add_node("tool_router", self._node_tool_router)
        graph.add_node("tool_exec", self._node_tool_exec)
        graph.add_node("observation", self._node_observation)
        graph.add_node("recovery", self._node_recovery)
        graph.add_node("replan", self._node_replan)
        graph.add_node("answer", self._node_answer)
        graph.add_node("persist_assistant_message", self._node_persist_assistant_message)
        graph.add_node("summary", self._node_summary)

        graph.add_edge(START, "load_memory")
        graph.add_edge("load_memory", "persist_user_message")
        graph.add_edge("persist_user_message", "intent")
        graph.add_edge("intent", "retrieve")
        graph.add_edge("retrieve", "plan")
        graph.add_conditional_edges(
            "plan",
            self._route_after_plan,
            {
                "tool_router": "tool_router",
                "answer": "answer",
            },
        )
        graph.add_edge("tool_router", "tool_exec")
        graph.add_conditional_edges(
            "tool_exec",
            self._route_after_tool_exec,
            {
                "tool_exec": "tool_exec",
                "observation": "observation",
                "answer": "answer",
            },
        )
        graph.add_edge("observation", "recovery")
        graph.add_edge("recovery", "replan")
        graph.add_conditional_edges(
            "replan",
            self._route_after_replan,
            {
                "tool_exec": "tool_exec",
                "answer": "answer",
            },
        )
        graph.add_edge("answer", "persist_assistant_message")
        graph.add_edge("persist_assistant_message", "summary")
        graph.add_edge("summary", END)
        return graph

    def _node_load_memory(self, state: AgentState) -> AgentState:
        state.mark("load_memory")
        existing_summary = self.repository.get_session_summary(state.session_id)
        if existing_summary and not self.session_service.get_summary(state.session_id):
            self.session_service.set_summary(state.session_id, existing_summary)
        return state

    def _node_persist_user_message(self, state: AgentState) -> AgentState:
        self.session_service.append_message(state.session_id, "user", state.user_query)
        self.repository.save_chat_message(state.session_id, "user", state.user_query)
        state.mark("persist_user_message")
        return state

    def _node_intent(self, state: AgentState) -> AgentState:
        state.intent = detect_intent(state.user_query)
        state.mark("intent")
        return state

    def _node_retrieve(self, state: AgentState) -> AgentState:
        retrieval = run_retrieval(state.user_query, self.retriever)
        state.context_text = retrieval.context_text
        state.sources = retrieval.sources
        state.retrieval_stage_latency_ms = dict(getattr(retrieval, "stage_latency_ms", {}) or {})
        state.mark("retrieve")
        return state

    def _node_plan(self, state: AgentState) -> AgentState:
        plan = create_plan(state.intent)
        state.plan_route = plan.route
        state.plan_steps = list(plan.steps or [])
        state.should_call_tool = bool(plan.should_call_tool or state.pending_tool_actions)
        if state.pending_tool_actions:
            state.plan_route = "tool"
        state.mark("plan")
        return state

    def _node_tool_router(self, state: AgentState) -> AgentState:
        actions = state.pending_tool_actions or [
            {"tool_name": action.tool_name, "tool_input": dict(action.tool_input)}
            for action in route_tools(state.user_query)
        ]
        state.pending_tool_actions = list(actions)
        tool_plan = create_tool_plan(
            [ToolAction(action["tool_name"], dict(action["tool_input"])) for action in state.pending_tool_actions]
        )
        state.plan_route = tool_plan.route
        state.plan_steps = list(tool_plan.steps or [])
        state.tool_actions = [
            {"tool_name": action["tool_name"], "tool_input": dict(action["tool_input"])}
            for action in state.pending_tool_actions
        ]
        if state.pending_tool_actions:
            first_action = state.pending_tool_actions[0]
            state.selected_tool = str(first_action["tool_name"])
            state.tool_input = dict(first_action["tool_input"])
        state.current_action_index = 0
        state.current_action = {}
        state.mark("tool_router")
        return state

    def _node_tool_exec(self, state: AgentState) -> AgentState:
        if state.current_action_index >= len(state.pending_tool_actions):
            state.last_tool_success = True
            return state
        action_payload = state.pending_tool_actions[state.current_action_index]
        action = ToolAction(
            tool_name=str(action_payload["tool_name"]),
            tool_input={str(key): str(value) for key, value in dict(action_payload["tool_input"]).items()},
        )
        state.current_action = {"tool_name": action.tool_name, "tool_input": dict(action.tool_input)}
        result = execute_tool(action.tool_name, action.tool_input, self.tool_registry)
        state.tool_output = asdict(result)
        state.tool_message = _append_tool_message(state.tool_message, result.message)
        status = "success" if result.success else "failed"
        state.tool_logs.append(
            {
                "tool_name": action.tool_name,
                "status": status,
                "message": result.message,
            }
        )
        state.observations.append(result.message)
        state.last_tool_success = result.success
        state.mark("tool_exec")
        self.repository.save_tool_log(
            session_id=state.session_id,
            tool_name=action.tool_name,
            input_payload=action.tool_input,
            output_payload=asdict(result),
            status=status,
        )
        if result.success:
            state.current_action_index += 1
        return state

    def _node_observation(self, state: AgentState) -> AgentState:
        state.observations.extend(observe_tool_result(self._tool_result_from_state(state)))
        state.mark("observation")
        return state

    def _node_recovery(self, state: AgentState) -> AgentState:
        result = self._tool_result_from_state(state)
        state.recovery_action = choose_recovery_action(result)
        state.mark("recovery")
        return state

    def _node_replan(self, state: AgentState) -> AgentState:
        current_action = ToolAction(
            tool_name=str(state.current_action.get("tool_name", "")),
            tool_input={str(key): str(value) for key, value in dict(state.current_action.get("tool_input", {})).items()},
        )
        result = self._tool_result_from_state(state)
        remaining_actions = [
            ToolAction(
                tool_name=str(action["tool_name"]),
                tool_input={str(key): str(value) for key, value in dict(action["tool_input"]).items()},
            )
            for action in state.pending_tool_actions[state.current_action_index + 1 :]
        ]
        state.recovery_action = choose_replan_action(current_action, state.recovery_action, remaining_actions, result)
        repaired_action = build_repaired_action(current_action.tool_name, result)
        replan_target = repaired_action
        if state.recovery_action == "fallback_to_remaining_actions" and remaining_actions:
            replan_target = remaining_actions[0]
        state.replan_steps = build_replan_steps(state.recovery_action, replan_target)
        if state.replan_steps:
            state.mark("replan")
        if repaired_action is not None:
            state.pending_tool_actions[state.current_action_index] = {
                "tool_name": repaired_action.tool_name,
                "tool_input": dict(repaired_action.tool_input),
            }
        elif state.recovery_action == "fallback_to_remaining_actions":
            state.current_action_index += 1
        else:
            state.current_action_index = len(state.pending_tool_actions)
        return state

    def _node_answer(self, state: AgentState) -> AgentState:
        state.answer_context_text = self._build_answer_context(state.session_id, state)
        state.mark("answer")
        return state

    def _node_persist_assistant_message(self, state: AgentState) -> AgentState:
        self.session_service.append_message(state.session_id, "assistant", state.final_answer)
        self.repository.save_chat_message(state.session_id, "assistant", state.final_answer)
        state.mark("persist_assistant_message")
        return state

    def _node_summary(self, state: AgentState) -> AgentState:
        summary = update_summary(
            self.summary_service,
            session_id=state.session_id,
            answer=state.final_answer,
            user_query=state.user_query,
        )
        state.summary = summary
        state.mark("summary")
        self.repository.save_session_summary(state.session_id, state.summary)
        return state

    def _route_after_plan(self, state: AgentState) -> str:
        return "tool_router" if state.should_call_tool else "answer"

    def _route_after_tool_exec(self, state: AgentState) -> str:
        if state.current_action_index >= len(state.pending_tool_actions):
            return "answer"
        if state.last_tool_success:
            return "tool_exec"
        return "observation"

    def _route_after_replan(self, state: AgentState) -> str:
        if state.recovery_action in {"retry_repaired_action", "fallback_to_remaining_actions"}:
            if state.current_action_index < len(state.pending_tool_actions):
                return "tool_exec"
        return "answer"

    def _finalize_state(self, session_id: str, user_query: str, state: AgentState, answer_result) -> AgentResponse:
        state.final_answer = answer_result.answer
        state.answer_backend = answer_result.answer_backend
        state.provider_status = answer_result.provider_status
        state.provider_error = answer_result.provider_error
        state.provider_attempts = answer_result.provider_attempts
        state.first_token_latency_ms = getattr(answer_result, "first_token_latency_ms", 0)
        state.total_latency_ms = getattr(answer_result, "total_latency_ms", 0)
        state.provider_diagnostic = getattr(answer_result, "provider_diagnostic", "")
        return AgentResponse(
            intent=state.intent,
            answer=state.final_answer,
            sources=state.sources,
            tool_logs=state.tool_logs,
            summary=state.summary,
            answer_backend=state.answer_backend,
            provider_status=state.provider_status,
            provider_error=state.provider_error,
            provider_attempts=state.provider_attempts,
            first_token_latency_ms=state.first_token_latency_ms,
            total_latency_ms=state.total_latency_ms,
            provider_diagnostic=state.provider_diagnostic,
            retrieval_stage_latency_ms=state.retrieval_stage_latency_ms,
            retrieval_backend=self.retriever.vector_store.backend_name(),
            embedding_backend=self.retriever.embedding_provider.backend_name(),
            reranker_backend=self.retriever.reranker.backend_name(),
            node_trace=state.node_trace,
            selected_tool=state.selected_tool,
            plan_route=state.plan_route,
            plan_steps=state.plan_steps,
            observations=state.observations,
            recovery_action=state.recovery_action,
            replan_steps=state.replan_steps,
            tool_actions=state.tool_actions,
        )

    def _build_answer_context(self, session_id: str, state: AgentState) -> str:
        parts: list[str] = []
        summary = self.session_service.get_summary(session_id).strip()
        if summary:
            parts.append(f"会话摘要：\n{summary}")

        recent_messages = self.session_service.get_recent_messages(session_id)
        if recent_messages:
            formatted_messages = []
            for message in recent_messages[-self.session_service.recent_limit :]:
                role = "用户" if message.get("role") == "user" else "助手"
                content = str(message.get("content", "")).strip()
                if content:
                    formatted_messages.append(f"{role}：{content}")
            if formatted_messages:
                parts.append("最近对话：\n" + "\n".join(formatted_messages))

        context_text = state.context_text.strip()
        if context_text:
            parts.append(f"知识库上下文：\n{context_text}")

        return "\n\n".join(parts).strip()

    def _tool_result_from_state(self, state: AgentState):
        payload = dict(state.tool_output)
        payload.setdefault("error_code", payload.get("code", ""))
        payload.setdefault("diagnostics", {})
        from app.models.tool_result import ToolResult

        return ToolResult(**payload)


def _append_tool_message(existing: str, message: str) -> str:
    if not existing:
        return message
    return f"{existing}\n{message}"
