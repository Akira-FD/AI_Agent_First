from __future__ import annotations


class SummaryService:
    def __init__(self, session_service, max_chars: int = 360) -> None:
        self.session_service = session_service
        self.max_chars = max_chars

    def update_summary(self, session_id: str, latest_answer: str, user_query: str = "") -> str:
        prior_summary = self.session_service.get_summary(session_id)
        parts = []
        if prior_summary:
            parts.append(prior_summary)
        if user_query:
            parts.append(f"本轮问题：{user_query}")
        if latest_answer:
            parts.append(f"最新结论：{latest_answer}")

        summary = "；".join(self._compact(part) for part in parts if part.strip())
        if len(summary) > self.max_chars:
            summary = summary[-self.max_chars :].lstrip("；。,.， ")
        self.session_service.set_summary(session_id, summary)
        return summary

    def _compact(self, text: str) -> str:
        return " ".join(text.split())
