import tempfile
import unittest
from pathlib import Path

from app.agent.graph import MVPAgent
from app.agent.state import AgentState
from app.agent.nodes.tool_router_node import ToolAction, route_tools
from app.config.settings import AppSettings
from app.rag.ingest_pipeline import IngestPipeline
from app.repositories.sqlite_repo import SQLiteRepository
from app.services.document_service import DocumentService
from app.services.llm_service import RuleBasedLLMService
from app.services.session_service import SessionService
from app.models.tool_result import ToolResult
from app.tools.base import ToolDefinition
from app.tools.registry import ToolRegistry


SAMPLE_DOC = """# Redis 文档

## 故障判断

当连接失败时，先检查 redis 进程是否存活，再查看错误日志。

# MySQL 文档

## 慢查询排查

先查看 slow query log，再结合 explain 分析索引命中情况。

# Kubernetes 文档

## Pod Terminating

当 Pod 一直处于 Terminating 状态时，先看 kubectl describe pod、事件和容器运行时日志。
"""


class ToolsAndAgentTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tempdir = tempfile.TemporaryDirectory()
        self.root = Path(self.tempdir.name)
        self.settings = AppSettings.from_root(self.root)
        (self.settings.docs_dir / "redis.md").write_text(SAMPLE_DOC, encoding="utf-8")
        self.repo = SQLiteRepository(self.settings.sqlite_path)
        IngestPipeline(settings=self.settings, repository=self.repo).ingest_directory(self.settings.docs_dir)
        self.agent = MVPAgent(
            settings=self.settings,
            repository=self.repo,
            session_service=SessionService(),
            document_service=DocumentService(self.repo),
            llm_service=RuleBasedLLMService(),
            tool_registry=ToolRegistry.with_defaults(),
        )

    def tearDown(self) -> None:
        self.tempdir.cleanup()

    def test_routes_troubleshoot_question_without_tool_call(self) -> None:
        response = self.agent.run(session_id="s1", user_query="Redis 连接失败时先做什么？")

        self.assertEqual(response.intent, "troubleshoot")
        self.assertFalse(response.tool_logs)
        self.assertIn("根据知识库", response.answer)

    def test_routes_operation_request_to_mock_tool(self) -> None:
        response = self.agent.run(session_id="s2", user_query="请帮我重启 redis 服务")

        self.assertEqual(response.intent, "execute")
        self.assertTrue(response.tool_logs)
        self.assertEqual(response.tool_logs[0]["tool_name"], "restart_mock_service")
        self.assertIn("已执行模拟工具", response.answer)

    def test_tool_router_builds_action_list_for_multi_step_request(self) -> None:
        actions = route_tools("请先查询 redis 状态，再查一下 timeout 相关日志")

        self.assertEqual([action.tool_name for action in actions], ["check_service_status", "search_error_logs"])
        self.assertEqual(actions[0].tool_input, {"service_name": "redis"})
        self.assertEqual(actions[1].tool_input, {"keyword": "timeout"})

    def test_tool_router_adds_incident_summary_action_for_summary_request(self) -> None:
        actions = route_tools("请先查询 redis 状态，再查一下 timeout 相关日志，最后给我总结根因")

        self.assertEqual(
            [action.tool_name for action in actions],
            ["check_service_status", "search_error_logs", "get_incident_summary"],
        )
        self.assertEqual(actions[2].tool_input, {"service_name": "redis", "keyword": "timeout"})

    def test_does_not_misfire_tool_for_explanatory_restart_question(self) -> None:
        response = self.agent.run(session_id="s3", user_query="解释一下 Redis 重启前为什么要确认写入任务")

        self.assertIn(response.intent, {"knowledge", "troubleshoot"})
        self.assertFalse(response.tool_logs)

    def test_does_not_misfire_tool_for_mysql_log_analysis_question(self) -> None:
        response = self.agent.run(session_id="s4", user_query="MySQL 慢查询排查时，应该先看什么日志和信息？")

        self.assertIn(response.intent, {"knowledge", "troubleshoot"})
        self.assertFalse(response.tool_logs)
        self.assertTrue(response.sources)
        self.assertIn("MySQL", response.sources[0]["section_path"])

    def test_routes_restart_tool_with_requested_service_name(self) -> None:
        response = self.agent.run(session_id="s5", user_query="请重启 mysql 服务")

        self.assertEqual(response.intent, "execute")
        self.assertTrue(response.tool_logs)
        self.assertIn("mysql", response.answer.lower())

    def test_agent_state_records_node_trace_for_knowledge_path(self) -> None:
        state = AgentState(session_id="s6", user_query="Redis 连接失败时先做什么？")

        self.assertEqual(state.session_id, "s6")
        self.assertEqual(state.user_query, "Redis 连接失败时先做什么？")
        self.assertEqual(state.node_trace, [])

        response = self.agent.run(session_id="s6", user_query=state.user_query)

        self.assertEqual(response.intent, "troubleshoot")
        self.assertIn("intent", response.node_trace)
        self.assertIn("retrieve", response.node_trace)
        self.assertIn("plan", response.node_trace)
        self.assertIn("answer", response.node_trace)
        self.assertIn("summary", response.node_trace)
        self.assertNotIn("tool_router", response.node_trace)
        self.assertNotIn("tool_exec", response.node_trace)

    def test_agent_state_records_tool_nodes_for_execute_path(self) -> None:
        response = self.agent.run(session_id="s7", user_query="请帮我重启 redis 服务")

        self.assertEqual(response.intent, "execute")
        self.assertEqual(response.plan_route, "tool")
        self.assertEqual(
            response.node_trace,
            [
                "load_memory",
                "persist_user_message",
                "intent",
                "retrieve",
                "plan",
                "tool_router",
                "tool_exec",
                "answer",
                "persist_assistant_message",
                "summary",
            ],
        )
        self.assertEqual(response.selected_tool, "restart_mock_service")

    def test_agent_plan_route_separates_knowledge_troubleshoot_and_execute(self) -> None:
        knowledge = self.agent.run(session_id="s8", user_query="解释一下 Redis maxmemory 的作用")
        troubleshoot = self.agent.run(session_id="s9", user_query="Redis 连接失败时怎么排查？")
        execute = self.agent.run(session_id="s10", user_query="请帮我重启 redis 服务")

        self.assertEqual(knowledge.plan_route, "answer")
        self.assertEqual(troubleshoot.plan_route, "diagnose")
        self.assertEqual(execute.plan_route, "tool")

    def test_agent_records_observation_and_recovery_for_failed_tool(self) -> None:
        class FailingRestartTool:
            definition = ToolDefinition(
                name="restart_mock_service",
                description="Always fails for recovery testing.",
            )

            def run(self, payload: dict[str, str]) -> ToolResult:
                return ToolResult(
                    success=False,
                    code="MOCK_FAILURE",
                    message="模拟重启失败，需要人工确认服务状态。",
                    data={"service_name": payload.get("service_name", "")},
                    retryable=False,
                )

        registry = ToolRegistry.with_defaults()
        registry.register("restart_mock_service", FailingRestartTool())
        agent = MVPAgent(
            settings=self.settings,
            repository=self.repo,
            session_service=SessionService(),
            document_service=DocumentService(self.repo),
            llm_service=RuleBasedLLMService(),
            tool_registry=registry,
        )

        response = agent.run(session_id="s11", user_query="请帮我重启 redis 服务")

        self.assertEqual(response.tool_logs[0]["status"], "failed")
        self.assertIn("observation", response.node_trace)
        self.assertIn("recovery", response.node_trace)
        self.assertIn("replan", response.node_trace)
        self.assertEqual(response.recovery_action, "degrade_to_answer")
        self.assertEqual(response.replan_steps, ["degrade_to_answer", "answer_with_available_context"])
        self.assertIn("模拟重启失败", response.observations[0])

    def test_agent_executes_multiple_tool_actions_in_order(self) -> None:
        response = self.agent.run(session_id="s12", user_query="请先查询 redis 状态，再查一下 timeout 相关日志")

        self.assertEqual(response.intent, "execute")
        self.assertEqual(response.plan_route, "tool")
        self.assertEqual(
            response.plan_steps,
            [
                "retrieve_context",
                "check_service_status",
                "search_error_logs",
                "answer_with_tool_results",
            ],
        )
        self.assertEqual(
            [log["tool_name"] for log in response.tool_logs],
            ["check_service_status", "search_error_logs"],
        )
        self.assertEqual(
            [action["tool_name"] for action in response.tool_actions],
            ["check_service_status", "search_error_logs"],
        )
        self.assertEqual(response.selected_tool, "check_service_status")
        self.assertEqual(response.node_trace.count("tool_exec"), 2)
        self.assertIn("服务 redis 当前状态为 running", response.observations[0])
        self.assertIn("timeout", response.observations[1])

    def test_agent_executes_status_logs_and_summary_chain(self) -> None:
        response = self.agent.run(
            session_id="s12b",
            user_query="请先查询 redis 状态，再查一下 timeout 相关日志，最后给我总结根因",
        )

        self.assertEqual(response.intent, "execute")
        self.assertEqual(response.plan_route, "tool")
        self.assertEqual(
            response.plan_steps,
            [
                "retrieve_context",
                "check_service_status",
                "search_error_logs",
                "get_incident_summary",
                "answer_with_tool_results",
            ],
        )
        self.assertEqual(
            [log["tool_name"] for log in response.tool_logs],
            ["check_service_status", "search_error_logs", "get_incident_summary"],
        )
        self.assertEqual(
            [action["tool_name"] for action in response.tool_actions],
            ["check_service_status", "search_error_logs", "get_incident_summary"],
        )
        self.assertEqual(response.node_trace.count("tool_exec"), 3)
        self.assertIn("摘要已生成", response.answer)

    def test_agent_recovers_retryable_validation_error_with_repaired_action(self) -> None:
        class AliasRepairTool:
            definition = ToolDefinition(
                name="check_service_status",
                description="Fails once with a repair hint then succeeds.",
            )

            def __init__(self) -> None:
                self.calls: list[dict[str, str]] = []

            def run(self, payload: dict[str, str]) -> ToolResult:
                self.calls.append(dict(payload))
                if "service_name" not in payload and "service" in payload:
                    return ToolResult(
                        success=False,
                        code="VALIDATION_ERROR",
                        message="工具参数校验失败，请根据结构化错误修正参数。",
                        data={
                            "missing_fields": ["service_name"],
                            "received_fields": ["service"],
                            "repaired_payload": {"service_name": payload["service"]},
                        },
                        retryable=True,
                    )
                return ToolResult(
                    success=True,
                    code="OK",
                    message=f"服务 {payload['service_name']} 当前状态为 running。",
                    data={"service_name": payload["service_name"], "status": "running"},
                )

        tool = AliasRepairTool()
        registry = ToolRegistry.with_defaults()
        registry.register("check_service_status", tool)
        agent = MVPAgent(
            settings=self.settings,
            repository=self.repo,
            session_service=SessionService(),
            document_service=DocumentService(self.repo),
            llm_service=RuleBasedLLMService(),
            tool_registry=registry,
        )

        response = agent.run(
            session_id="s13",
            user_query="请检查 redis 状态",
            tool_actions=[ToolAction("check_service_status", {"service": "redis"})],
        )

        self.assertEqual(response.recovery_action, "retry_repaired_action")
        self.assertEqual(
            response.replan_steps,
            ["retry_repaired_action", "check_service_status", "answer_with_tool_results"],
        )
        self.assertEqual(response.node_trace.count("tool_exec"), 2)
        self.assertEqual(response.node_trace.count("recovery"), 1)
        self.assertEqual(response.node_trace.count("replan"), 1)
        self.assertEqual([log["status"] for log in response.tool_logs], ["failed", "success"])
        self.assertEqual(tool.calls, [{"service": "redis"}, {"service_name": "redis"}])
        self.assertIn("running", response.observations[-1])

    def test_agent_stops_remaining_actions_after_degrade_replan(self) -> None:
        class FailingStatusTool:
            definition = ToolDefinition(
                name="check_service_status",
                description="Fails and forces degrade-to-answer replan.",
            )

            def run(self, payload: dict[str, str]) -> ToolResult:
                return ToolResult(
                    success=False,
                    code="STATUS_CHECK_FAILED",
                    message="状态检查失败，无法继续执行后续运维动作。",
                    data={"service_name": payload.get("service_name", "")},
                    retryable=False,
                )

        class TrackingLogTool:
            definition = ToolDefinition(
                name="search_error_logs",
                description="Tracks whether the second action executed.",
            )

            def __init__(self) -> None:
                self.calls: list[dict[str, str]] = []

            def run(self, payload: dict[str, str]) -> ToolResult:
                self.calls.append(dict(payload))
                return ToolResult(
                    success=True,
                    code="OK",
                    message="日志检查已执行。",
                    data={"keyword": payload.get("keyword", "")},
                )

        tracking_tool = TrackingLogTool()
        registry = ToolRegistry.with_defaults()
        registry.register("check_service_status", FailingStatusTool())
        registry.register("search_error_logs", tracking_tool)
        agent = MVPAgent(
            settings=self.settings,
            repository=self.repo,
            session_service=SessionService(),
            document_service=DocumentService(self.repo),
            llm_service=RuleBasedLLMService(),
            tool_registry=registry,
        )

        response = agent.run(
            session_id="s14",
            user_query="请先查询 redis 状态，再查一下 timeout 相关日志",
        )

        self.assertEqual(response.recovery_action, "degrade_to_answer")
        self.assertEqual(response.replan_steps, ["degrade_to_answer", "answer_with_available_context"])
        self.assertEqual(response.node_trace.count("tool_exec"), 1)
        self.assertEqual([log["tool_name"] for log in response.tool_logs], ["check_service_status"])
        self.assertEqual(tracking_tool.calls, [])

    def test_agent_stops_remaining_actions_after_retry_later_replan(self) -> None:
        class RetryLaterTool:
            definition = ToolDefinition(
                name="check_service_status",
                description="Returns retryable error without repaired payload.",
            )

            def run(self, payload: dict[str, str]) -> ToolResult:
                return ToolResult(
                    success=False,
                    code="UPSTREAM_UNAVAILABLE",
                    message="状态源暂时不可用，请稍后重试。",
                    data={"service_name": payload.get("service_name", "")},
                    retryable=True,
                )

        class TrackingRestartTool:
            definition = ToolDefinition(
                name="restart_mock_service",
                description="Tracks whether restart action executed.",
            )

            def __init__(self) -> None:
                self.calls: list[dict[str, str]] = []

            def run(self, payload: dict[str, str]) -> ToolResult:
                self.calls.append(dict(payload))
                return ToolResult(
                    success=True,
                    code="OK",
                    message="已执行模拟工具。",
                    data={"service_name": payload.get("service_name", "")},
                )

        tracking_tool = TrackingRestartTool()
        registry = ToolRegistry.with_defaults()
        registry.register("check_service_status", RetryLaterTool())
        registry.register("restart_mock_service", tracking_tool)
        agent = MVPAgent(
            settings=self.settings,
            repository=self.repo,
            session_service=SessionService(),
            document_service=DocumentService(self.repo),
            llm_service=RuleBasedLLMService(),
            tool_registry=registry,
        )

        response = agent.run(
            session_id="s15",
            user_query="请先查询 redis 状态，再重启 redis 服务",
            tool_actions=[
                ToolAction("check_service_status", {"service_name": "redis"}),
                ToolAction("restart_mock_service", {"service_name": "redis"}),
            ],
        )

        self.assertEqual(response.recovery_action, "retry_later")
        self.assertEqual(response.replan_steps, ["retry_later", "answer_with_retry_guidance"])
        self.assertEqual(response.node_trace.count("tool_exec"), 1)
        self.assertEqual([log["tool_name"] for log in response.tool_logs], ["check_service_status"])
        self.assertEqual(tracking_tool.calls, [])

    def test_agent_replans_to_remaining_log_action_after_status_check_failure(self) -> None:
        class FailingStatusTool:
            definition = ToolDefinition(
                name="check_service_status",
                description="Fails but should allow log-search fallback.",
            )

            def run(self, payload: dict[str, str]) -> ToolResult:
                return ToolResult(
                    success=False,
                    code="STATUS_CHECK_FAILED",
                    message="状态检查失败，请改为直接查看错误日志。",
                    data={"service_name": payload.get("service_name", "")},
                    retryable=False,
                )

        class TrackingLogTool:
            definition = ToolDefinition(
                name="search_error_logs",
                description="Tracks the fallback log-search action.",
            )

            def __init__(self) -> None:
                self.calls: list[dict[str, str]] = []

            def run(self, payload: dict[str, str]) -> ToolResult:
                self.calls.append(dict(payload))
                return ToolResult(
                    success=True,
                    code="OK",
                    message=f"已找到与 {payload.get('keyword', '')} 相关的 2 条模拟日志。",
                    data={"keyword": payload.get("keyword", ""), "hits": 2},
                )

        tracking_tool = TrackingLogTool()
        registry = ToolRegistry.with_defaults()
        registry.register("check_service_status", FailingStatusTool())
        registry.register("search_error_logs", tracking_tool)
        agent = MVPAgent(
            settings=self.settings,
            repository=self.repo,
            session_service=SessionService(),
            document_service=DocumentService(self.repo),
            llm_service=RuleBasedLLMService(),
            tool_registry=registry,
        )

        response = agent.run(
            session_id="s16",
            user_query="请先查询 redis 状态，再查一下 timeout 相关日志",
        )

        self.assertEqual(response.recovery_action, "fallback_to_remaining_actions")
        self.assertEqual(
            response.replan_steps,
            ["fallback_to_remaining_actions", "search_error_logs", "answer_with_tool_results"],
        )
        self.assertEqual(response.node_trace.count("tool_exec"), 2)
        self.assertEqual(
            [log["tool_name"] for log in response.tool_logs],
            ["check_service_status", "search_error_logs"],
        )
        self.assertEqual(tracking_tool.calls, [{"keyword": "timeout"}])


if __name__ == "__main__":
    unittest.main()
