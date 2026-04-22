from __future__ import annotations


def route_tool(user_query: str) -> tuple[str, dict[str, str]]:
    lowered = user_query.lower()
    if "重启" in lowered or "restart" in lowered:
        return "restart_mock_service", {"service_name": "redis"}
    if "日志" in lowered:
        return "search_error_logs", {"keyword": "error"}
    return "check_service_status", {"service_name": "redis"}
