import tempfile
import unittest
from pathlib import Path

from app.tools.ops_tools import (
    CheckServiceStatusTool,
    CommandResult,
    ControlledToolRuntime,
    RestartMockServiceTool,
    SearchErrorLogsTool,
)


class FakeCommandRunner:
    def __init__(self, result: CommandResult) -> None:
        self.result = result
        self.calls: list[dict[str, object]] = []

    def run(self, command: list[str], timeout_seconds: int) -> CommandResult:
        self.calls.append({"command": list(command), "timeout_seconds": timeout_seconds})
        return self.result


class RealToolAdaptersTests(unittest.TestCase):
    def test_check_service_status_uses_controlled_real_runner(self) -> None:
        runtime = ControlledToolRuntime(
            root_dir=Path.cwd(),
            real_tools_enabled=True,
            restart_enabled=False,
            allowed_services={"redis"},
            log_dirs=(),
            command_timeout_seconds=5,
            command_runner=FakeCommandRunner(
                CommandResult(
                    returncode=0,
                    stdout='{"Name":"Redis","DisplayName":"Redis Service","Status":"Running"}',
                    stderr="",
                )
            ),
        )

        result = CheckServiceStatusTool(runtime=runtime).run({"service_name": "redis"})

        self.assertTrue(result.success)
        self.assertEqual(result.code, "OK")
        self.assertEqual(result.error_code, "OK")
        self.assertEqual(result.data["mode"], "real")
        self.assertEqual(result.data["service_name"], "redis")
        self.assertEqual(result.data["matched_name"], "Redis")
        self.assertEqual(result.data["status"], "Running")
        self.assertIn("adapter", result.diagnostics)
        self.assertIn("timeout_seconds", result.diagnostics)

    def test_search_error_logs_scans_controlled_log_directories(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            log_dir = root / "data" / "logs"
            log_dir.mkdir(parents=True, exist_ok=True)
            (log_dir / "redis.log").write_text(
                "\n".join(
                    [
                        "2026-04-26 10:00:00 INFO startup complete",
                        "2026-04-26 10:05:00 ERROR timeout while talking to upstream",
                    ]
                ),
                encoding="utf-8",
            )
            runtime = ControlledToolRuntime(
                root_dir=root,
                real_tools_enabled=True,
                restart_enabled=False,
                allowed_services={"redis"},
                log_dirs=(log_dir,),
                command_timeout_seconds=5,
            )

            result = SearchErrorLogsTool(runtime=runtime).run({"keyword": "timeout"})

            self.assertTrue(result.success)
            self.assertEqual(result.data["mode"], "real")
            self.assertEqual(result.data["hits"], 1)
            self.assertEqual(result.data["scanned_files"], 1)
            self.assertIn("timeout", result.data["matches"][0]["line"].lower())

    def test_restart_tool_returns_dry_run_when_real_restart_is_disabled(self) -> None:
        runtime = ControlledToolRuntime(
            root_dir=Path.cwd(),
            real_tools_enabled=True,
            restart_enabled=False,
            allowed_services={"redis"},
            log_dirs=(),
            command_timeout_seconds=5,
            command_runner=FakeCommandRunner(
                CommandResult(returncode=0, stdout="", stderr="")
            ),
        )

        result = RestartMockServiceTool(runtime=runtime).run({"service_name": "redis"})

        self.assertTrue(result.success)
        self.assertEqual(result.code, "DRY_RUN")
        self.assertEqual(result.error_code, "DRY_RUN")
        self.assertEqual(result.data["mode"], "dry_run")
        self.assertIn("未实际执行", result.message)
        self.assertIn("suggested_command", result.diagnostics)


if __name__ == "__main__":
    unittest.main()
