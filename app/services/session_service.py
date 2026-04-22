from __future__ import annotations

from collections import defaultdict


class SessionService:
    def __init__(self, recent_limit: int = 10) -> None:
        self.recent_limit = recent_limit
        self._messages: dict[str, list[dict[str, str]]] = defaultdict(list)
        self._summaries: dict[str, str] = {}

    def append_message(self, session_id: str, role: str, content: str) -> None:
        self._messages[session_id].append({"role": role, "content": content})
        self._messages[session_id] = self._messages[session_id][-self.recent_limit :]

    def get_recent_messages(self, session_id: str) -> list[dict[str, str]]:
        return list(self._messages.get(session_id, []))

    def set_summary(self, session_id: str, summary: str) -> None:
        self._summaries[session_id] = summary

    def get_summary(self, session_id: str) -> str:
        return self._summaries.get(session_id, "")
