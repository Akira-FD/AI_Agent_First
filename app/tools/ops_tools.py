from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Protocol
import json
import re
import subprocess

from app.models.tool_result import ToolResult
from app.tools.base import ToolDefinition
from app.tools.validators import validate_tool_input


SERVICE_ALIASES = {"service_name": ["service", "serviceName", "name", "服务名"]}
LOG_FILE_PATTERNS = ("*.log", "*.txt", "*.out")


def validation_error_result(error: dict[str, object]) -> ToolResult:
    return ToolResult(
        success=False,
        code="VALIDATION_ERROR",
        message="工具参数校验失败，请根据结构化错误修正参数。",
        data=error,
        retryable=True,
    )


@dataclass(frozen=True)
class CommandResult:
    returncode: int
    stdout: str
    stderr: str


class CommandRunner(Protocol):
    def run(self, command: list[str], timeout_seconds: int) -> CommandResult:
        ...


class SubprocessCommandRunner:
    def run(self, command: list[str], timeout_seconds: int) -> CommandResult:
        completed = subprocess.run(
            command,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="ignore",
            timeout=timeout_seconds,
            shell=False,
        )
        return CommandResult(
            returncode=completed.returncode,
            stdout=completed.stdout.strip(),
            stderr=completed.stderr.strip(),
        )


@dataclass
class ControlledToolRuntime:
    root_dir: Path
    real_tools_enabled: bool = False
    restart_enabled: bool = False
    allowed_services: set[str] = field(default_factory=set)
    log_dirs: tuple[Path, ...] = ()
    command_timeout_seconds: int = 5
    command_runner: CommandRunner | None = None

    @classmethod
    def from_settings(cls, settings, command_runner: CommandRunner | None = None) -> "ControlledToolRuntime":
        raw_allowed_services = getattr(settings, "tool_allowed_services", ())
        if isinstance(raw_allowed_services, str):
            raw_allowed_services = tuple(item.strip() for item in raw_allowed_services.split(",") if item.strip())
        raw_log_dirs = getattr(settings, "tool_log_dirs", ())
        resolved_log_dirs: list[Path] = []
        for raw_path in raw_log_dirs:
            path = Path(raw_path)
            if not path.is_absolute():
                path = (Path(getattr(settings, "root_dir", Path.cwd())) / path).resolve()
            resolved_log_dirs.append(path)
        return cls(
            root_dir=Path(getattr(settings, "root_dir", Path.cwd())).resolve(),
            real_tools_enabled=bool(getattr(settings, "real_tools_enabled", False)),
            restart_enabled=bool(getattr(settings, "tool_restart_enabled", False)),
            allowed_services={_normalize_service_name(item) for item in raw_allowed_services if str(item).strip()},
            log_dirs=tuple(resolved_log_dirs),
            command_timeout_seconds=max(1, int(getattr(settings, "tool_command_timeout_seconds", 5))),
            command_runner=command_runner or SubprocessCommandRunner(),
        )

    def is_service_allowed(self, service_name: str) -> bool:
        normalized = _normalize_service_name(service_name)
        return not self.allowed_services or normalized in self.allowed_services

    def runner(self) -> CommandRunner:
        return self.command_runner or SubprocessCommandRunner()


@dataclass
class CheckServiceStatusTool:
    runtime: ControlledToolRuntime | None = None
    definition: ToolDefinition = field(
        default_factory=lambda: ToolDefinition(
            name="check_service_status",
            description="Check the current health of a local service using a controlled adapter.",
        )
    )

    def run(self, payload: dict[str, str]) -> ToolResult:
        valid, repaired, error = validate_tool_input(payload, ["service_name"], SERVICE_ALIASES)
        if not valid or repaired is None:
            return validation_error_result(error or {})
        service_name = repaired["service_name"]
        if not self.runtime or not self.runtime.real_tools_enabled:
            return _mock_status_result(service_name)
        if not self.runtime.is_service_allowed(service_name):
            return ToolResult(
                success=False,
                code="SERVICE_NOT_ALLOWED",
                message=f"服务 {service_name} 不在受控状态检查白名单中。",
                data={"service_name": service_name, "mode": "real"},
                retryable=False,
            )
        try:
            command = _build_service_status_command(service_name)
            result = self.runtime.runner().run(command, timeout_seconds=self.runtime.command_timeout_seconds)
            if result.returncode != 0:
                details = result.stderr or result.stdout or "service lookup failed"
                return ToolResult(
                    success=False,
                    code="SERVICE_LOOKUP_FAILED",
                    message=f"受控状态检查失败：{details}",
                    data={"service_name": service_name, "mode": "real"},
                    retryable=False,
                )
            service_info = _parse_service_json(result.stdout, service_name)
            status = str(service_info.get("Status", "unknown"))
            matched_name = str(service_info.get("Name", service_name))
            display_name = str(service_info.get("DisplayName", matched_name))
            return ToolResult(
                success=True,
                code="OK",
                message=f"服务 {display_name} 当前状态为 {status}。",
                data={
                    "service_name": service_name,
                    "matched_name": matched_name,
                    "display_name": display_name,
                    "status": status,
                    "mode": "real",
                },
            )
        except Exception as exc:
            return ToolResult(
                success=False,
                code="SERVICE_LOOKUP_FAILED",
                message=f"受控状态检查失败：{exc}",
                data={"service_name": service_name, "mode": "real"},
                retryable=False,
            )


@dataclass
class SearchErrorLogsTool:
    runtime: ControlledToolRuntime | None = None
    definition: ToolDefinition = field(
        default_factory=lambda: ToolDefinition(
            name="search_error_logs",
            description="Search controlled local log directories by keyword.",
        )
    )

    def run(self, payload: dict[str, str]) -> ToolResult:
        valid, repaired, error = validate_tool_input(payload, ["keyword"], {"keyword": ["query", "q", "关键词"]})
        if not valid or repaired is None:
            return validation_error_result(error or {})
        keyword = repaired["keyword"]
        if not self.runtime or not self.runtime.real_tools_enabled:
            return _mock_log_result(keyword)
        scanned_files = 0
        matches: list[dict[str, object]] = []
        lowered_keyword = keyword.lower()
        for log_dir in self.runtime.log_dirs:
            if not log_dir.exists():
                continue
            for pattern in LOG_FILE_PATTERNS:
                for log_file in log_dir.rglob(pattern):
                    scanned_files += 1
                    try:
                        for line_number, line in enumerate(log_file.read_text(encoding="utf-8", errors="ignore").splitlines(), start=1):
                            if lowered_keyword not in line.lower():
                                continue
                            matches.append(
                                {
                                    "file": str(log_file),
                                    "line_number": line_number,
                                    "line": line.strip(),
                                }
                            )
                            if len(matches) >= 20:
                                break
                    except OSError:
                        continue
                    if len(matches) >= 20:
                        break
                if len(matches) >= 20:
                    break
            if len(matches) >= 20:
                break
        return ToolResult(
            success=True,
            code="OK" if matches else "NO_MATCHES",
            message=(
                f"已在受控日志目录中找到 {len(matches)} 条与 {keyword} 相关的真实日志。"
                if matches
                else f"已扫描受控日志目录，但未找到与 {keyword} 相关的真实日志。"
            ),
            data={
                "keyword": keyword,
                "hits": len(matches),
                "scanned_files": scanned_files,
                "matches": matches,
                "mode": "real",
            },
        )


@dataclass
class RestartMockServiceTool:
    runtime: ControlledToolRuntime | None = None
    definition: ToolDefinition = field(
        default_factory=lambda: ToolDefinition(
            name="restart_mock_service",
            description="Controlled service restart adapter with dry-run by default.",
        )
    )

    def run(self, payload: dict[str, str]) -> ToolResult:
        valid, repaired, error = validate_tool_input(payload, ["service_name"], SERVICE_ALIASES)
        if not valid or repaired is None:
            return validation_error_result(error or {})
        service_name = repaired["service_name"]
        if not self.runtime or not self.runtime.real_tools_enabled:
            return _mock_restart_result(service_name)
        if not self.runtime.is_service_allowed(service_name):
            return ToolResult(
                success=False,
                code="SERVICE_NOT_ALLOWED",
                message=f"服务 {service_name} 不在受控重启白名单中。",
                data={"service_name": service_name, "mode": "real"},
                retryable=False,
            )
        if not self.runtime.restart_enabled:
            command_preview = " ".join(_build_restart_service_command(service_name))
            return ToolResult(
                success=True,
                code="DRY_RUN",
                message=f"受控重启未开启，未实际执行。建议人工确认后执行：{command_preview}",
                data={
                    "service_name": service_name,
                    "status": "dry_run",
                    "mode": "dry_run",
                    "suggested_command": command_preview,
                },
            )
        try:
            command = _build_restart_service_command(service_name)
            result = self.runtime.runner().run(command, timeout_seconds=self.runtime.command_timeout_seconds)
            if result.returncode != 0:
                details = result.stderr or result.stdout or "restart failed"
                return ToolResult(
                    success=False,
                    code="RESTART_FAILED",
                    message=f"受控重启失败：{details}",
                    data={"service_name": service_name, "mode": "real"},
                    retryable=False,
                )
            service_info = _parse_service_json(result.stdout, service_name)
            status = str(service_info.get("Status", "unknown"))
            matched_name = str(service_info.get("Name", service_name))
            display_name = str(service_info.get("DisplayName", matched_name))
            return ToolResult(
                success=True,
                code="OK",
                message=f"已执行受控重启，{display_name} 当前状态为 {status}。",
                data={
                    "service_name": service_name,
                    "matched_name": matched_name,
                    "display_name": display_name,
                    "status": status,
                    "mode": "real",
                },
            )
        except Exception as exc:
            return ToolResult(
                success=False,
                code="RESTART_FAILED",
                message=f"受控重启失败：{exc}",
                data={"service_name": service_name, "mode": "real"},
                retryable=False,
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
        service_name = payload.get("service_name", "service")
        keyword = payload.get("keyword", "关键错误")
        summary = f"{service_name} 出现与 {keyword} 相关的问题，建议优先检查状态、日志与近期变更。"
        return ToolResult(
            success=True,
            code="OK",
            message=f"事件 {incident_id} 摘要已生成。",
            data={"incident_id": incident_id, "summary": summary, "service_name": service_name, "keyword": keyword},
        )


def _normalize_service_name(service_name: str) -> str:
    return service_name.strip().lower()


def _sanitize_service_name(service_name: str) -> str:
    normalized = _normalize_service_name(service_name)
    if not re.fullmatch(r"[a-z0-9_.-]+", normalized):
        raise ValueError("unsupported service name")
    return normalized


def _build_service_status_command(service_name: str) -> list[str]:
    safe_name = _sanitize_service_name(service_name)
    script = (
        f"$serviceName='{safe_name}'; "
        "$matches = Get-Service | Where-Object { $_.Name -like ('*' + $serviceName + '*') -or $_.DisplayName -like ('*' + $serviceName + '*') } | "
        "Select-Object -First 5 Name,DisplayName,Status; "
        "if (-not $matches) { exit 3 }; "
        "$matches | ConvertTo-Json -Compress"
    )
    return ["powershell.exe", "-NoProfile", "-Command", script]


def _build_restart_service_command(service_name: str) -> list[str]:
    safe_name = _sanitize_service_name(service_name)
    script = (
        f"$serviceName='{safe_name}'; "
        "Restart-Service -Name $serviceName -ErrorAction Stop; "
        "Get-Service -Name $serviceName | Select-Object Name,DisplayName,Status | ConvertTo-Json -Compress"
    )
    return ["powershell.exe", "-NoProfile", "-Command", script]


def _parse_service_json(raw_output: str, requested_service: str) -> dict[str, object]:
    payload = json.loads(raw_output)
    if isinstance(payload, list):
        requested = _normalize_service_name(requested_service)
        exact = next(
            (
                item
                for item in payload
                if isinstance(item, dict) and _normalize_service_name(str(item.get("Name", ""))) == requested
            ),
            None,
        )
        if exact is not None:
            return exact
        first = payload[0] if payload else {}
        return first if isinstance(first, dict) else {}
    return payload if isinstance(payload, dict) else {}


def _mock_status_result(service_name: str) -> ToolResult:
    return ToolResult(
        success=True,
        code="OK",
        message=f"服务 {service_name} 当前状态为 running。",
        data={"service_name": service_name, "status": "running", "mode": "mock"},
    )


def _mock_log_result(keyword: str) -> ToolResult:
    return ToolResult(
        success=True,
        code="OK",
        message=f"已找到与 {keyword} 相关的 2 条模拟日志。",
        data={"keyword": keyword, "hits": 2, "mode": "mock"},
    )


def _mock_restart_result(service_name: str) -> ToolResult:
    return ToolResult(
        success=True,
        code="OK",
        message=f"已执行模拟工具，{service_name} 服务重启成功。",
        data={"service_name": service_name, "status": "restarted", "mode": "mock"},
    )
