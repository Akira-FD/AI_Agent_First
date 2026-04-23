from __future__ import annotations


SERVICE_NAMES = ("redis", "mysql", "kubernetes", "pod", "nginx", "elasticsearch", "prometheus")


def route_tool(user_query: str) -> tuple[str, dict[str, str]]:
    lowered = user_query.lower()
    service_name = _extract_service_name(lowered)
    if "重启" in lowered or "restart" in lowered:
        return "restart_mock_service", {"service_name": service_name}
    if "日志" in lowered or "log" in lowered:
        return "search_error_logs", {"keyword": _extract_log_keyword(lowered, service_name)}
    return "check_service_status", {"service_name": service_name}


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
