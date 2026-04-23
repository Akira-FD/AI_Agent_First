from __future__ import annotations


class ChatPage:
    def __init__(self, agent=None, session_id: str = "default") -> None:
        self.agent = agent
        self.session_id = session_id
        self.messages: list[dict[str, str]] = []
        self.sources: list[dict[str, object]] = []
        self.tool_logs: list[dict[str, str]] = []

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
        return response
