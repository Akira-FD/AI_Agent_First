from __future__ import annotations

from dataclasses import dataclass, field
from dataclasses import asdict

from app.agent.nodes.answer_node import build_answer
from app.agent.nodes.intent_node import detect_intent
from app.agent.nodes.plan_node import should_call_tool
from app.agent.nodes.retrieve_node import run_retrieval
from app.agent.nodes.summary_node import update_summary
from app.agent.nodes.tool_exec_node import execute_tool
from app.agent.nodes.tool_router_node import route_tool
from app.rag.retriever import Retriever
from app.services.summary_service import SummaryService


@dataclass
class AgentResponse:
    intent: str
    answer: str
    sources: list[dict[str, str]] = field(default_factory=list)
    tool_logs: list[dict[str, str]] = field(default_factory=list)
    summary: str = ""


class MVPAgent:
    def __init__(
        self,
        settings,
        repository,
        session_service,
        document_service,
        llm_service,
        tool_registry,
    ) -> None:
        self.settings = settings
        self.repository = repository
        self.session_service = session_service
        self.document_service = document_service
        self.llm_service = llm_service
        self.tool_registry = tool_registry
        self.retriever = Retriever(repository=repository, top_k=settings.retrieval_top_k)
        self.summary_service = SummaryService(session_service)

    def run(self, session_id: str, user_query: str) -> AgentResponse:
        self.session_service.append_message(session_id, "user", user_query)
        self.repository.save_chat_message(session_id, "user", user_query)
        intent = detect_intent(user_query)
        retrieval = run_retrieval(user_query, self.retriever)

        tool_logs: list[dict[str, str]] = []
        tool_message: str | None = None
        if should_call_tool(intent):
            tool_name, tool_input = route_tool(user_query)
            result = execute_tool(tool_name, tool_input, self.tool_registry)
            tool_message = result.message
            status = "success" if result.success else "failed"
            tool_logs.append(
                {
                    "tool_name": tool_name,
                    "status": status,
                    "message": result.message,
                }
            )
            self.repository.save_tool_log(
                session_id=session_id,
                tool_name=tool_name,
                input_payload=tool_input,
                output_payload=asdict(result),
                status=status,
            )

        answer = build_answer(
            llm_service=self.llm_service,
            user_query=user_query,
            context_text=retrieval.context_text,
            tool_message=tool_message,
        )
        self.session_service.append_message(session_id, "assistant", answer)
        self.repository.save_chat_message(session_id, "assistant", answer)
        summary = update_summary(self.summary_service, session_id=session_id, answer=answer)
        return AgentResponse(
            intent=intent,
            answer=answer,
            sources=retrieval.sources,
            tool_logs=tool_logs,
            summary=summary,
        )
