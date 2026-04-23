import os
import tempfile
import time
import unittest
from pathlib import Path
from types import SimpleNamespace

from app.main import bootstrap_application
from app.rag.ingest_pipeline import IngestPipeline
from app.ui.main_window import MainWindow


class PyQtWindowTests(unittest.TestCase):
    def test_main_window_can_send_message_and_render_response(self) -> None:
        os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
        from PyQt6.QtWidgets import QApplication

        app_instance = QApplication.instance() or QApplication([])
        with tempfile.TemporaryDirectory() as tmpdir:
            app = bootstrap_application(Path(tmpdir))
            (app.settings.docs_dir / "redis.md").write_text(
                "# Redis\n\n## 重启\n\n重启前先确认没有高风险写入。",
                encoding="utf-8",
            )
            IngestPipeline(settings=app.settings, repository=app.repository).ingest_directory(app.settings.docs_dir)
            window = MainWindow(agent=app.agent, settings=app.settings, document_service=app.document_service)

            window.input_box.setPlainText("请重启 redis 服务")
            window.handle_send()

            deadline = time.monotonic() + 2.0
            while "已执行模拟工具" not in window.chat_history.toPlainText():
                if time.monotonic() > deadline:
                    self.fail("Timed out waiting for desktop response.")
                app_instance.processEvents()
                time.sleep(0.02)

            self.assertIn("请重启 redis 服务", window.chat_history.toPlainText())
            self.assertIn("已执行模拟工具", window.chat_history.toPlainText())
            self.assertIn("Redis", window.sources_panel.toPlainText())
            self.assertIn("restart_mock_service", window.tool_logs_panel.toPlainText())
            app_instance.processEvents()

    def test_main_window_sends_requests_without_blocking_ui(self) -> None:
        os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
        from PyQt6.QtWidgets import QApplication

        class SlowChatPage:
            def __init__(self) -> None:
                self.messages = []

            def send_message(self, content: str):
                self.messages.append({"role": "user", "content": content})
                time.sleep(0.25)
                self.messages.append({"role": "assistant", "content": "异步回答已返回"})
                return SimpleNamespace(
                    answer="异步回答已返回",
                    sources=[
                        {
                            "title": "Redis 故障排查",
                            "source": "redis.md",
                            "section_path": "Redis > 故障排查",
                            "score": 4.2,
                            "excerpt": "先检查连接与资源占用。",
                        }
                    ],
                    tool_logs=[],
                )

        app_instance = QApplication.instance() or QApplication([])
        with tempfile.TemporaryDirectory() as tmpdir:
            app = bootstrap_application(Path(tmpdir))
            window = MainWindow(
                agent=app.agent,
                settings=app.settings,
                document_service=app.document_service,
                llm_service=app.llm_service,
            )
            window.chat_page = SlowChatPage()

            window.input_box.setPlainText("Redis 连接超时时先看什么？")
            started_at = time.monotonic()
            window.handle_send()
            elapsed = time.monotonic() - started_at

            self.assertLess(elapsed, 0.15)
            self.assertFalse(window.send_button.isEnabled())
            self.assertIn("处理中", window.request_status.text())

            deadline = time.monotonic() + 2.0
            while "异步回答已返回" not in window.chat_history.toPlainText():
                if time.monotonic() > deadline:
                    self.fail("Timed out waiting for async UI response.")
                app_instance.processEvents()
                time.sleep(0.02)

            self.assertTrue(window.send_button.isEnabled())
            self.assertIn("Redis > 故障排查", window.sources_panel.toPlainText())

    def test_main_window_streams_assistant_output_progressively(self) -> None:
        os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
        from PyQt6.QtWidgets import QApplication

        class FastChatPage:
            def __init__(self) -> None:
                self.messages = []

            def send_message(self, content: str):
                self.messages.append({"role": "user", "content": content})
                answer = "第一步检查 Redis 连接数；第二步检查 maxmemory；第三步查看 slowlog。"
                self.messages.append({"role": "assistant", "content": answer})
                return SimpleNamespace(answer=answer, sources=[], tool_logs=[])

        app_instance = QApplication.instance() or QApplication([])
        with tempfile.TemporaryDirectory() as tmpdir:
            app = bootstrap_application(Path(tmpdir))
            window = MainWindow(
                agent=app.agent,
                settings=app.settings,
                document_service=app.document_service,
                llm_service=app.llm_service,
            )
            window.chat_page = FastChatPage()
            window._stream_chunk_size = 4
            window._stream_interval_ms = 10

            window.input_box.setPlainText("Redis OOM 怎么排查？")
            window.handle_send()

            deadline = time.monotonic() + 2.0
            partial_snapshot = ""
            while time.monotonic() < deadline:
                app_instance.processEvents()
                time.sleep(0.02)
                text = window.chat_history.toPlainText()
                if "助手：" in text and "slowlog" not in text:
                    partial_snapshot = text
                    break

            self.assertIn("助手：", partial_snapshot)
            self.assertNotIn("slowlog", partial_snapshot)
            self.assertIn("输出中", window.request_status.text())

            deadline = time.monotonic() + 2.0
            while "slowlog" not in window.chat_history.toPlainText():
                if time.monotonic() > deadline:
                    self.fail("Timed out waiting for streamed answer.")
                app_instance.processEvents()
                time.sleep(0.02)

            self.assertIn("状态：已完成", window.request_status.text())

    def test_main_window_can_cancel_request_and_ignore_late_response(self) -> None:
        os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
        from PyQt6.QtWidgets import QApplication

        class SlowChatPage:
            def __init__(self) -> None:
                self.messages = []

            def send_message(self, content: str):
                self.messages.append({"role": "user", "content": content})
                time.sleep(0.25)
                answer = "这个回答不应该在取消后出现在界面中。"
                self.messages.append({"role": "assistant", "content": answer})
                return SimpleNamespace(answer=answer, sources=[], tool_logs=[])

        app_instance = QApplication.instance() or QApplication([])
        with tempfile.TemporaryDirectory() as tmpdir:
            app = bootstrap_application(Path(tmpdir))
            window = MainWindow(
                agent=app.agent,
                settings=app.settings,
                document_service=app.document_service,
                llm_service=app.llm_service,
            )
            window.chat_page = SlowChatPage()

            window.input_box.setPlainText("MySQL 日志异常先看什么？")
            window.handle_send()
            window.cancel_current_request()

            self.assertIn("已取消", window.request_status.text())

            deadline = time.monotonic() + 2.0
            while window._request_thread is not None:
                if time.monotonic() > deadline:
                    self.fail("Timed out waiting for canceled worker cleanup.")
                app_instance.processEvents()
                time.sleep(0.02)

            self.assertNotIn("这个回答不应该", window.chat_history.toPlainText())
            self.assertTrue(window.send_button.isEnabled())
            self.assertTrue(window.retry_button.isEnabled())

    def test_main_window_shows_timeout_and_retry_replays_last_query(self) -> None:
        os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
        from PyQt6.QtWidgets import QApplication

        class TimeoutThenRetryChatPage:
            def __init__(self) -> None:
                self.calls = []
                self.mode = "slow"

            def send_message(self, content: str):
                self.calls.append(content)
                if self.mode == "slow":
                    time.sleep(0.2)
                    return SimpleNamespace(answer="超时后的旧回答", sources=[], tool_logs=[])
                return SimpleNamespace(answer="重试后的新回答", sources=[], tool_logs=[])

        app_instance = QApplication.instance() or QApplication([])
        with tempfile.TemporaryDirectory() as tmpdir:
            app = bootstrap_application(Path(tmpdir))
            window = MainWindow(
                agent=app.agent,
                settings=app.settings,
                document_service=app.document_service,
                llm_service=app.llm_service,
            )
            chat_page = TimeoutThenRetryChatPage()
            window.chat_page = chat_page
            window._request_timeout_ms = 50

            window.input_box.setPlainText("Kubernetes Pod 重启频繁怎么办？")
            window.handle_send()

            deadline = time.monotonic() + 2.0
            while "超时" not in window.request_status.text():
                if time.monotonic() > deadline:
                    self.fail("Timed out waiting for request timeout state.")
                app_instance.processEvents()
                time.sleep(0.02)

            self.assertTrue(window.retry_button.isEnabled())

            deadline = time.monotonic() + 2.0
            while window._request_thread is not None:
                if time.monotonic() > deadline:
                    self.fail("Timed out waiting for timed out worker cleanup.")
                app_instance.processEvents()
                time.sleep(0.02)

            chat_page.mode = "fast"
            window.retry_last_query()

            deadline = time.monotonic() + 2.0
            while "重试后的新回答" not in window.chat_history.toPlainText():
                if time.monotonic() > deadline:
                    self.fail("Timed out waiting for retried response.")
                app_instance.processEvents()
                time.sleep(0.02)

            self.assertEqual(chat_page.calls.count("Kubernetes Pod 重启频繁怎么办？"), 2)
            self.assertNotIn("超时后的旧回答", window.chat_history.toPlainText())


if __name__ == "__main__":
    unittest.main()
