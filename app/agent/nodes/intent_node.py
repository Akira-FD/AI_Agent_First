from __future__ import annotations


def detect_intent(user_query: str) -> str:
    lowered = user_query.lower()
    action_keywords = ("重启", "restart", "执行", "check", "查询状态", "日志")
    if any(keyword in lowered for keyword in action_keywords):
        return "execute"
    if "报错" in lowered or "故障" in lowered or "失败" in lowered:
        return "troubleshoot"
    return "knowledge"
