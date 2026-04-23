import tempfile
import unittest
from pathlib import Path

from app.agent.graph import MVPAgent
from app.config.settings import AppSettings
from app.rag.ingest_pipeline import IngestPipeline
from app.repositories.sqlite_repo import SQLiteRepository
from app.services.document_service import DocumentService
from app.services.llm_service import RuleBasedLLMService
from app.services.session_service import SessionService
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


if __name__ == "__main__":
    unittest.main()
