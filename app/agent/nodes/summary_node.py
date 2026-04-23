from __future__ import annotations

from app.services.summary_service import SummaryService


def update_summary(summary_service: SummaryService, session_id: str, answer: str, user_query: str = "") -> str:
    return summary_service.update_summary(
        session_id=session_id,
        latest_answer=answer,
        user_query=user_query,
    )
