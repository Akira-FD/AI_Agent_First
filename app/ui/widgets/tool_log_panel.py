from __future__ import annotations

from html import escape


class ToolLogPanel:
    def __init__(self) -> None:
        self.logs: list[dict[str, str]] = []

    def add_log(self, log: dict[str, str]) -> None:
        self.logs.append(log)

    def render_text(self) -> str:
        if not self.logs:
            return "暂无工具调用"
        return "\n".join(
            f"{log.get('tool_name', 'unknown')} [{log.get('status', 'unknown')}] {log.get('message', '')}"
            for log in self.logs
        )

    def render_html(self) -> str:
        if not self.logs:
            return "<div class='tool-log-empty'>暂无工具调用</div>"
        cards: list[str] = []
        for log in self.logs:
            tool_name = escape(str(log.get("tool_name", "unknown")))
            status = escape(str(log.get("status", "unknown")))
            message = escape(str(log.get("message", ""))).replace("\n", "<br>")
            cards.append(
                "<div class='tool-log-card'>"
                "<div class='tool-log-header'>"
                f"<div class='tool-name'>{tool_name}</div>"
                f"<div class='status-pill'>{status}</div>"
                "</div>"
                f"<div class='tool-log-message'>{message}</div>"
                "</div>"
            )
        return "".join(cards)
