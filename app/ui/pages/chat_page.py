from __future__ import annotations


class ChatPage:
    def __init__(self, agent=None, session_id: str = "default") -> None:
        self.agent = agent
        self.session_id = session_id
        self.messages: list[dict[str, str]] = []
        self.sources: list[dict[str, object]] = []
        self.tool_logs: list[dict[str, str]] = []
        self.summary: str = ""
        self.retrieval_backend: str = "unknown"
        self.embedding_backend: str = "unknown"
        self.reranker_backend: str = "unknown"
        self.node_trace: list[str] = []
        self.plan_route: str = ""
        self.plan_steps: list[str] = []
        self.tool_actions: list[dict[str, object]] = []
        self.recovery_action: str = ""
        self.replan_steps: list[str] = []

    def add_message(self, role: str, content: str) -> None:
        self.messages.append({"role": role, "content": content})

    def send_message(self, content: str):
        if self.agent is None:
            raise RuntimeError("ChatPage requires an agent before sending messages.")
        self.add_message("user", content)
        response = self.agent.run(session_id=self.session_id, user_query=content)
        self.add_message("assistant", response.answer)
        self.sources = list(response.sources)
        self.tool_logs = list(response.tool_logs)
        self.summary = getattr(response, "summary", "")
        self.retrieval_backend = getattr(response, "retrieval_backend", "unknown")
        self.embedding_backend = getattr(response, "embedding_backend", "unknown")
        self.reranker_backend = getattr(response, "reranker_backend", "unknown")
        self.node_trace = list(getattr(response, "node_trace", []))
        self.plan_route = getattr(response, "plan_route", "")
        self.plan_steps = list(getattr(response, "plan_steps", []))
        self.tool_actions = list(getattr(response, "tool_actions", []))
        self.recovery_action = getattr(response, "recovery_action", "")
        self.replan_steps = list(getattr(response, "replan_steps", []))
        return response
