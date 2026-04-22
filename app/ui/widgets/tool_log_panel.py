from __future__ import annotations


class ToolLogPanel:
    def __init__(self) -> None:
        self.logs: list[dict[str, str]] = []

    def add_log(self, log: dict[str, str]) -> None:
        self.logs.append(log)
