from __future__ import annotations

from dataclasses import dataclass, field

from app.models.tool_result import ToolResult
from app.tools.base import ToolDefinition
from app.tools.validators import validate_tool_input


SERVICE_ALIASES = {"service_name": ["service", "serviceName", "name", "服务名"]}


def validation_error_result(error: dict[str, object]) -> ToolResult:
    return ToolResult(
        success=False,
        code="VALIDATION_ERROR",
        message="工具参数校验失败，请根据结构化错误修正参数。",
        data=error,
        retryable=True,
    )


@dataclass
class CheckServiceStatusTool:
    definition: ToolDefinition = field(
        default_factory=lambda: ToolDefinition(
            name="check_service_status",
            description="Check the current health of a local mock service.",
        )
    )

    def run(self, payload: dict[str, str]) -> ToolResult:
        valid, repaired, error = validate_tool_input(payload, ["service_name"], SERVICE_ALIASES)
        if not valid or repaired is None:
            return validation_error_result(error or {})
        service_name = repaired["service_name"]
        return ToolResult(
            success=True,
            code="OK",
            message=f"服务 {service_name} 当前状态为 running。",
            data={"service_name": service_name, "status": "running"},
        )


@dataclass
class SearchErrorLogsTool:
    definition: ToolDefinition = field(
        default_factory=lambda: ToolDefinition(
            name="search_error_logs",
            description="Search mock incident logs by keyword.",
        )
    )

    def run(self, payload: dict[str, str]) -> ToolResult:
        valid, repaired, error = validate_tool_input(payload, ["keyword"], {"keyword": ["query", "q", "关键词"]})
        if not valid or repaired is None:
            return validation_error_result(error or {})
        keyword = repaired["keyword"]
        return ToolResult(
            success=True,
            code="OK",
            message=f"已找到与 {keyword} 相关的 2 条模拟日志。",
            data={"keyword": keyword, "hits": 2},
        )


@dataclass
class RestartMockServiceTool:
    definition: ToolDefinition = field(
        default_factory=lambda: ToolDefinition(
            name="restart_mock_service",
            description="Restart a mock service for demo purposes.",
        )
    )

    def run(self, payload: dict[str, str]) -> ToolResult:
        valid, repaired, error = validate_tool_input(payload, ["service_name"], SERVICE_ALIASES)
        if not valid or repaired is None:
            return validation_error_result(error or {})
        service_name = repaired["service_name"]
        return ToolResult(
            success=True,
            code="OK",
            message=f"已执行模拟工具，{service_name} 服务重启成功。",
            data={"service_name": service_name, "status": "restarted"},
        )


@dataclass
class GetIncidentSummaryTool:
    definition: ToolDefinition = field(
        default_factory=lambda: ToolDefinition(
            name="get_incident_summary",
            description="Return a fixed incident summary for the MVP demo.",
        )
    )

    def run(self, payload: dict[str, str]) -> ToolResult:
        incident_id = payload.get("incident_id", "INC-001")
        return ToolResult(
            success=True,
            code="OK",
            message=f"事件 {incident_id} 摘要已生成。",
            data={"incident_id": incident_id, "summary": "Redis latency spike due to memory pressure."},
        )
