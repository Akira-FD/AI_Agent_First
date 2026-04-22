from __future__ import annotations


class ChatPage:
    def __init__(self) -> None:
        self.messages: list[dict[str, str]] = []

    def add_message(self, role: str, content: str) -> None:
        self.messages.append({"role": role, "content": content})
