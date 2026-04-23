from __future__ import annotations


EXPLANATION_HINTS = ("解释", "为什么", "原因", "如何分析", "先看什么", "看什么", "怎么排查", "排查")
EXECUTION_PATTERNS = (
    "请帮我重启",
    "帮我重启",
    "重启 ",
    "restart ",
    "请执行",
    "执行 ",
    "请先查询",
    "先查询",
    "再查一下",
    "帮我查一下",
    "查询状态",
    "check ",
)


def detect_intent(user_query: str) -> str:
    lowered = user_query.lower()
    if any(hint in user_query for hint in EXPLANATION_HINTS):
        if "失败" in user_query or "报错" in user_query or "故障" in user_query:
            return "troubleshoot"
        return "knowledge"

    if any(pattern in lowered for pattern in EXECUTION_PATTERNS):
        return "execute"
    if "报错" in lowered or "故障" in lowered or "失败" in lowered:
        return "troubleshoot"
    return "knowledge"
