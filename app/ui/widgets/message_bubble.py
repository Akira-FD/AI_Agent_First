from __future__ import annotations

from html import escape


class MessageBubble:
    def __init__(self, role: str, content: str) -> None:
        self.role = role
        self.content = content

    def render_html(self) -> str:
        role = self.role if self.role in {"user", "assistant", "system"} else "assistant"
        role_label = {
            "user": "用户：",
            "assistant": "助手：",
            "system": "系统：",
        }[role]
        safe_content = escape(self.content or "").replace("\n", "<br>")
        if not safe_content:
            safe_content = "<span class='message-placeholder'>...</span>"
        alignment_class = "message-row user-row" if role == "user" else "message-row assistant-row"
        return (
            f"<div class='{alignment_class}'>"
            f"<div class='message-bubble {role}-bubble'>"
            f"<div class='message-role'>{escape(role_label)}</div>"
            f"<div class='message-content'>{safe_content}</div>"
            "</div>"
            "</div>"
        )
