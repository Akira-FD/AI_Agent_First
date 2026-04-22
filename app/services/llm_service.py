from __future__ import annotations


class RuleBasedLLMService:
    def generate_answer(self, user_query: str, context_text: str, tool_message: str | None = None) -> str:
        if tool_message:
            return f"已根据请求执行操作。{tool_message}\n\n结合知识库上下文：\n{context_text or '暂无知识库上下文。'}"
        return f"根据知识库，针对“{user_query}”的建议如下：\n{context_text or '暂无可用上下文，请先导入文档。'}"
