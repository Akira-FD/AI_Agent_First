import tempfile
import unittest
from pathlib import Path

from app.main import bootstrap_application
from app.rag.ingest_pipeline import IngestPipeline
from app.ui.pages.chat_page import ChatPage
from app.ui.pages.docs_page import DocsPage
from app.ui.widgets.source_card import SourceCard
from app.ui.widgets.tool_log_panel import ToolLogPanel


class UIBehaviorTests(unittest.TestCase):
    def test_chat_page_sends_query_and_updates_messages_sources_and_tool_logs(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            app = bootstrap_application(Path(tmpdir))
            (app.settings.docs_dir / "redis.md").write_text(
                "# Redis\n\n## 重启\n\n重启前先确认无高风险写入。",
                encoding="utf-8",
            )
            IngestPipeline(settings=app.settings, repository=app.repository).ingest_directory(app.settings.docs_dir)
            chat_page = ChatPage(agent=app.agent, session_id="ui-test")

            response = chat_page.send_message("请重启 redis 服务")

            self.assertEqual(chat_page.messages[0]["role"], "user")
            self.assertEqual(chat_page.messages[-1]["role"], "assistant")
            self.assertTrue(chat_page.sources)
            self.assertTrue(chat_page.tool_logs)
            self.assertIn("已执行模拟工具", response.answer)
            self.assertIn(response.answer_backend, {"remote", "fallback"})

    def test_chat_page_exposes_answer_backend_metadata(self) -> None:
        class FakeAgent:
            def run(self, session_id: str, user_query: str):
                return type(
                    "AgentResponse",
                    (),
                    {
                        "answer": "这是远程模型回答。",
                        "sources": [],
                        "tool_logs": [],
                        "answer_backend": "remote",
                        "provider_status": "success",
                        "provider_error": "",
                        "provider_attempts": 1,
                        "reranker_backend": "bge",
                        "node_trace": ["intent", "retrieve", "plan", "answer"],
                        "plan_route": "answer",
                        "plan_steps": ["retrieve_context", "answer_with_context"],
                        "tool_actions": [],
                        "recovery_action": "none",
                        "replan_steps": [],
                    },
                )()

        chat_page = ChatPage(agent=FakeAgent(), session_id="ui-test")

        response = chat_page.send_message("测试问题")

        self.assertEqual(response.answer_backend, "remote")
        self.assertEqual(response.provider_status, "success")
        self.assertEqual(chat_page.reranker_backend, "bge")
        self.assertEqual(chat_page.node_trace, ["intent", "retrieve", "plan", "answer"])
        self.assertEqual(chat_page.plan_route, "answer")
        self.assertEqual(chat_page.plan_steps, ["retrieve_context", "answer_with_context"])
        self.assertEqual(chat_page.tool_actions, [])
        self.assertEqual(chat_page.recovery_action, "none")
        self.assertEqual(chat_page.replan_steps, [])
        self.assertEqual(chat_page.messages[-1]["role"], "assistant")

    def test_docs_page_loads_document_metadata_for_sidebar(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            app = bootstrap_application(Path(tmpdir))
            (app.settings.docs_dir / "redis.md").write_text("# Redis\n\n## 状态\n\n检查状态。", encoding="utf-8")
            IngestPipeline(settings=app.settings, repository=app.repository).ingest_directory(app.settings.docs_dir)

            docs_page = DocsPage(document_service=app.document_service)
            documents = docs_page.refresh()

            self.assertEqual(len(documents), 1)
            self.assertEqual(documents[0]["source"], "redis.md")
            self.assertGreater(documents[0]["chunk_count"], 0)

    def test_source_card_and_tool_log_panel_render_display_text(self) -> None:
        source = SourceCard(
            {
                "title": "重启",
                "source": "redis.md",
                "section_path": "Redis > 重启",
                "score": 3.2,
                "excerpt": "重启前先检查状态。",
            }
        )
        panel = ToolLogPanel()
        panel.add_log({"tool_name": "restart_mock_service", "status": "success", "message": "ok"})

        self.assertIn("Redis > 重启", source.render_text())
        self.assertIn("restart_mock_service", panel.render_text())


if __name__ == "__main__":
    unittest.main()
