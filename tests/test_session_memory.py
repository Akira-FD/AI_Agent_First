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


class RecordingLLMService(RuleBasedLLMService):
    def __init__(self) -> None:
        self.calls: list[dict[str, str]] = []

    def generate_answer_result(self, user_query: str, context_text: str, tool_message: str | None = None):
        self.calls.append(
            {
                "user_query": user_query,
                "context_text": context_text,
                "tool_message": tool_message or "",
            }
        )
        return super().generate_answer_result(
            user_query=user_query,
            context_text=context_text,
            tool_message=tool_message,
        )


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

    def test_agent_includes_summary_and_recent_messages_in_answer_context(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            settings = AppSettings.from_root(root)
            repo = SQLiteRepository(settings.sqlite_path)
            session = SessionService(recent_limit=3)
            llm_service = RecordingLLMService()
            agent = MVPAgent(
                settings=settings,
                repository=repo,
                session_service=session,
                document_service=DocumentService(repo),
                llm_service=llm_service,
                tool_registry=ToolRegistry.with_defaults(),
            )

            session.set_summary("s3", "用户之前一直在排查 Redis timeout。")
            session.append_message("s3", "user", "上一轮问过 Redis 连接池是否耗尽。")
            session.append_message("s3", "assistant", "建议优先查看连接数与超时配置。")

            agent.run("s3", "这次如果继续排查，我应该先看什么？")

            self.assertTrue(llm_service.calls)
            context_text = llm_service.calls[-1]["context_text"]
            self.assertIn("会话摘要", context_text)
            self.assertIn("Redis timeout", context_text)
            self.assertIn("最近对话", context_text)
            self.assertIn("连接池", context_text)


if __name__ == "__main__":
    unittest.main()
