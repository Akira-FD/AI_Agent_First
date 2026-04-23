from __future__ import annotations


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
