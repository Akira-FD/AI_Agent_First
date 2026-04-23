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


class PersistenceTests(unittest.TestCase):
    def test_repository_persists_chat_messages_and_tool_logs(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            repo = SQLiteRepository(Path(tmpdir) / "app.db")

            repo.save_chat_message("s1", "user", "hello")
            repo.save_chat_message("s1", "assistant", "world")
            repo.save_tool_log("s1", "restart_mock_service", {"service_name": "redis"}, {"success": True}, "success")

            self.assertEqual(len(repo.list_chat_sessions()), 1)
            self.assertEqual(len(repo.list_chat_messages("s1")), 2)
            self.assertEqual(len(repo.list_tool_logs("s1")), 1)

    def test_agent_persists_conversation_and_tool_execution(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            settings = AppSettings.from_root(root)
            (settings.docs_dir / "redis.md").write_text(
                "# Redis\n\n## 重启\n\n重启前先检查状态。",
                encoding="utf-8",
            )
            repo = SQLiteRepository(settings.sqlite_path)
            IngestPipeline(settings=settings, repository=repo).ingest_directory(settings.docs_dir)
            agent = MVPAgent(
                settings=settings,
                repository=repo,
                session_service=SessionService(),
                document_service=DocumentService(repo),
                llm_service=RuleBasedLLMService(),
                tool_registry=ToolRegistry.with_defaults(),
            )

            agent.run("s2", "请重启 redis 服务")

            self.assertEqual(len(repo.list_chat_messages("s2")), 2)
            self.assertEqual(len(repo.list_tool_logs("s2")), 1)


if __name__ == "__main__":
    unittest.main()
