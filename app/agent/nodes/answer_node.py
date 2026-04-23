from __future__ import annotations

from app.services.llm_service import LLMAnswerResult, RuleBasedLLMService


def build_answer(
    llm_service: RuleBasedLLMService,
    user_query: str,
    context_text: str,
    tool_message: str | None = None,
) -> LLMAnswerResult:
    return llm_service.generate_answer_result(
        user_query=user_query,
        context_text=context_text,
        tool_message=tool_message,
    )
