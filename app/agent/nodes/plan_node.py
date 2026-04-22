from __future__ import annotations


def should_call_tool(intent: str) -> bool:
    return intent == "execute"
