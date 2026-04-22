from __future__ import annotations


class SummaryService:
    def __init__(self, session_service) -> None:
        self.session_service = session_service

    def update_summary(self, session_id: str, latest_answer: str) -> str:
        summary = latest_answer[:160]
        self.session_service.set_summary(session_id, summary)
        return summary
