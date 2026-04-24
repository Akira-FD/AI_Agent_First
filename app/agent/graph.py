from __future__ import annotations

from dataclasses import dataclass, field
from dataclasses import asdict

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

    def run(self, session_id: str, user_query: str, tool_actions: list[ToolAction] | None = None) -> AgentResponse:
        return self._run_internal(session_id=session_id, user_query=user_query, tool_actions=tool_actions)

    def stream(self, session_id: str, user_query: str, tool_actions: list[ToolAction] | None = None):
        state = self._prepare_state(session_id=session_id, user_query=user_query, tool_actions=tool_actions)
        final_result = None
        backend_label = ""
        if hasattr(self.llm_service, "backend_label"):
            backend_label = str(self.llm_service.backend_label())
        if hasattr(self.llm_service, "stream_answer_result") and backend_label.startswith("openai-compatible:"):
            for event in self.llm_service.stream_answer_result(
                user_query=user_query,
                context_text=state.context_text,
                tool_message=state.tool_message or None,
            ):
                if event.type == "delta":
                    yield {"type": "delta", "delta": event.delta}
                elif event.type == "done":
                    final_result = event.result
                    break
        if final_result is None:
            answer_result = build_answer(
                llm_service=self.llm_service,
                user_query=user_query,
                context_text=state.context_text,
                tool_message=state.tool_message or None,
            )
            final_result = answer_result
        response = self._finalize_state(
            session_id=session_id,
            user_query=user_query,
            state=state,
            answer_result=final_result,
        )
        yield {"type": "done", "response": response}

    def _run_internal(self, session_id: str, user_query: str, tool_actions: list[ToolAction] | None = None) -> AgentResponse:
        state = self._prepare_state(session_id=session_id, user_query=user_query, tool_actions=tool_actions)
        answer_result = build_answer(
            llm_service=self.llm_service,
            user_query=user_query,
            context_text=state.context_text,
            tool_message=state.tool_message or None,
        )
        return self._finalize_state(
            session_id=session_id,
            user_query=user_query,
            state=state,
            answer_result=answer_result,
        )

    def _prepare_state(self, session_id: str, user_query: str, tool_actions: list[ToolAction] | None = None) -> AgentState:
        state = AgentState(session_id=session_id, user_query=user_query)

        state.mark("load_memory")
        existing_summary = self.repository.get_session_summary(session_id)
        if existing_summary and not self.session_service.get_summary(session_id):
            self.session_service.set_summary(session_id, existing_summary)

        self.session_service.append_message(session_id, "user", user_query)
        self.repository.save_chat_message(session_id, "user", user_query)
        state.mark("persist_user_message")

        state.intent = detect_intent(user_query)
        state.mark("intent")

        retrieval = run_retrieval(user_query, self.retriever)
        state.context_text = retrieval.context_text
        state.sources = retrieval.sources
        state.retrieval_stage_latency_ms = dict(getattr(retrieval, "stage_latency_ms", {}) or {})
        state.mark("retrieve")

        plan = create_plan(state.intent)
        state.plan_route = plan.route
        state.plan_steps = list(plan.steps or [])
        if tool_actions:
            state.plan_route = "tool"
        state.mark("plan")
        if plan.should_call_tool or tool_actions:
            actions = tool_actions or route_tools(user_query)
            tool_plan = create_tool_plan(actions)
            state.plan_route = tool_plan.route
            state.plan_steps = list(tool_plan.steps or [])
            state.tool_actions = [
                {"tool_name": action.tool_name, "tool_input": action.tool_input}
                for action in actions
            ]
            first_action = actions[0]
            state.selected_tool = first_action.tool_name
            state.tool_input = first_action.tool_input
            state.mark("tool_router")
            for index, action in enumerate(actions):
                result = self._execute_action(session_id, state, action)
                if not result.success:
                    state.observations.extend(observe_tool_result(result))
                    state.mark("observation")
                    state.recovery_action = choose_recovery_action(result)
                    state.mark("recovery")
                    remaining_actions = actions[index + 1 :]
                    state.recovery_action = choose_replan_action(action, state.recovery_action, remaining_actions, result)
                    repaired_action = build_repaired_action(action.tool_name, result)
                    replan_target = repaired_action
                    if state.recovery_action == "fallback_to_remaining_actions" and remaining_actions:
                        replan_target = remaining_actions[0]
                    state.replan_steps = build_replan_steps(state.recovery_action, replan_target)
                    if state.replan_steps:
                        state.mark("replan")
                    if repaired_action is not None:
                        self._execute_action(session_id, state, repaired_action)
                        continue
                    if state.recovery_action == "fallback_to_remaining_actions":
                        continue
                    if state.recovery_action in {"degrade_to_answer", "retry_later"}:
                        break
        return state

    def _finalize_state(self, session_id: str, user_query: str, state: AgentState, answer_result) -> AgentResponse:
        state.final_answer = answer_result.answer
        state.answer_backend = answer_result.answer_backend
        state.provider_status = answer_result.provider_status
        state.provider_error = answer_result.provider_error
        state.provider_attempts = answer_result.provider_attempts
        state.first_token_latency_ms = getattr(answer_result, "first_token_latency_ms", 0)
        state.total_latency_ms = getattr(answer_result, "total_latency_ms", 0)
        state.provider_diagnostic = getattr(answer_result, "provider_diagnostic", "")
        state.mark("answer")

        self.session_service.append_message(session_id, "assistant", state.final_answer)
        self.repository.save_chat_message(session_id, "assistant", state.final_answer)
        state.mark("persist_assistant_message")

        summary = update_summary(
            self.summary_service,
            session_id=session_id,
            answer=state.final_answer,
            user_query=user_query,
        )
        state.summary = summary
        state.mark("summary")
        self.repository.save_session_summary(session_id, state.summary)
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

    def _execute_action(self, session_id: str, state: AgentState, action: ToolAction):
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
        state.mark("tool_exec")
        self.repository.save_tool_log(
            session_id=session_id,
            tool_name=action.tool_name,
            input_payload=action.tool_input,
            output_payload=asdict(result),
            status=status,
        )
        return result


def _append_tool_message(existing: str, message: str) -> str:
    if not existing:
        return message
    return f"{existing}\n{message}"
