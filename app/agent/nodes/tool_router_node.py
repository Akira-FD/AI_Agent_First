from __future__ import annotations

from dataclasses import dataclass


SERVICE_NAMES = ("redis", "mysql", "kubernetes", "pod", "nginx", "elasticsearch", "prometheus")


@dataclass(frozen=True)
class ToolAction:
    tool_name: str
    tool_input: dict[str, str]


def route_tool(user_query: str) -> tuple[str, dict[str, str]]:
    action = route_tools(user_query)[0]
    return action.tool_name, action.tool_input


def route_tools(user_query: str) -> list[ToolAction]:
    lowered = user_query.lower()
    service_name = _extract_service_name(lowered)
    log_keyword = _extract_log_keyword(lowered, service_name)
    actions: list[ToolAction] = []

    if _asks_for_status(lowered):
        actions.append(ToolAction("check_service_status", {"service_name": service_name}))
    if _asks_for_logs(lowered):
        actions.append(ToolAction("search_error_logs", {"keyword": log_keyword}))
    if "重启" in lowered or "restart" in lowered:
        actions.append(ToolAction("restart_mock_service", {"service_name": service_name}))
    if _asks_for_summary(lowered):
        actions.append(ToolAction("get_incident_summary", {"service_name": service_name, "keyword": log_keyword}))
    if actions:
        return _dedupe_actions(actions)
    return [ToolAction("check_service_status", {"service_name": service_name})]


def _asks_for_status(lowered_query: str) -> bool:
    return any(pattern in lowered_query for pattern in ("状态", "status", "查询", "查一下", "check"))


def _asks_for_logs(lowered_query: str) -> bool:
    return "日志" in lowered_query or "log" in lowered_query


def _asks_for_summary(lowered_query: str) -> bool:
    return any(pattern in lowered_query for pattern in ("总结", "汇总", "summary", "根因"))


def _extract_service_name(lowered_query: str) -> str:
    for service_name in SERVICE_NAMES:
        if service_name in lowered_query:
            return "kubernetes" if service_name == "pod" else service_name
    return "redis"


def _extract_log_keyword(lowered_query: str, service_name: str) -> str:
    if "oom" in lowered_query:
        return "oom"
    if "timeout" in lowered_query:
        return "timeout"
    if "slow query" in lowered_query or "慢查询" in lowered_query:
        return "slow query"
    return service_name


def _dedupe_actions(actions: list[ToolAction]) -> list[ToolAction]:
    deduped: list[ToolAction] = []
    seen: set[tuple[str, tuple[tuple[str, str], ...]]] = set()
    for action in actions:
        key = (action.tool_name, tuple(sorted(action.tool_input.items())))
        if key in seen:
            continue
        seen.add(key)
        deduped.append(action)
    return deduped
