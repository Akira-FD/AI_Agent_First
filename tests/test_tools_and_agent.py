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


if __name__ == "__main__":
    unittest.main()
