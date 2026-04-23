import tempfile
import unittest
from pathlib import Path

from app.agent.graph import MVPAgent
from app.config.settings import AppSettings
from app.repositories.sqlite_repo import SQLiteRepository
from app.services.document_service import DocumentService
from app.services.llm_service import RuleBasedLLMService
from app.services.session_service import SessionService
from app.services.summary_service import SummaryService
from app.tools.registry import ToolRegistry


class SessionMemoryTests(unittest.TestCase):
    def test_summary_combines_prior_summary_latest_question_and_answer(self) -> None:
        session = SessionService()
        session.set_summary("s1", "用户正在排查 Redis OOM。")
        service = SummaryService(session_service=session)

        summary = service.update_summary(
            session_id="s1",
            user_query="下一步应该检查哪些 Redis 配置？",
            latest_answer="建议先检查 maxmemory、eviction policy、slowlog 和内存碎片率。",
        )

        self.assertIn("Redis OOM", summary)
        self.assertIn("下一步应该检查哪些 Redis 配置", summary)
        self.assertIn("maxmemory", summary)
        self.assertLessEqual(len(summary), 360)

    def test_repository_persists_session_summary(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "app.db"
            repo = SQLiteRepository(db_path)

            repo.save_session_summary("s1", "用户目标：排查 Kubernetes CrashLoopBackOff。")
            reopened = SQLiteRepository(db_path)

            self.assertEqual(
                reopened.get_session_summary("s1"),
                "用户目标：排查 Kubernetes CrashLoopBackOff。",
            )

    def test_agent_updates_and_persists_conversation_summary(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            settings = AppSettings.from_root(root)
            repo = SQLiteRepository(settings.sqlite_path)
            session = SessionService()
            agent = MVPAgent(
                settings=settings,
                repository=repo,
                session_service=session,
                document_service=DocumentService(repo),
                llm_service=RuleBasedLLMService(),
                tool_registry=ToolRegistry.with_defaults(),
            )

            response = agent.run("s2", "Redis OOM 时应该先检查什么？")

            self.assertIn("Redis OOM", response.summary)
            self.assertIn("Redis OOM", session.get_summary("s2"))
            self.assertEqual(repo.get_session_summary("s2"), response.summary)


if __name__ == "__main__":
    unittest.main()
