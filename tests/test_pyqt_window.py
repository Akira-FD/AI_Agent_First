import os
import tempfile
import time
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from app.main import bootstrap_application
from app.rag.ingest_pipeline import IngestPipeline
from app.ui.main_window import MainWindow, launch_pyqt_app


class PyQtWindowTests(unittest.TestCase):
    def test_launch_pyqt_app_centers_window_and_uses_large_desktop_size(self) -> None:
        os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
        from PyQt6.QtWidgets import QApplication

        with tempfile.TemporaryDirectory() as tmpdir:
            app = bootstrap_application(Path(tmpdir))
            app_instance = QApplication.instance() or QApplication([])

            with patch.object(app_instance, "exec", return_value=0):
                with patch.object(app_instance, "primaryScreen", return_value=None):
                    with patch.object(MainWindow, "show"), patch.object(MainWindow, "center_on_screen", autospec=True) as center_on_screen:
                        result = launch_pyqt_app(
                            app.agent,
                            app.settings,
                            app.document_service,
                            app.llm_service,
                        )

            launched_window = center_on_screen.call_args[0][0] if center_on_screen.call_args else None
            self.assertEqual(result, 0)
            self.assertIsInstance(launched_window, MainWindow)
            self.assertGreaterEqual(launched_window.width(), launched_window.minimumWidth())
            self.assertGreaterEqual(launched_window.height(), launched_window.minimumHeight())

    def test_main_window_uses_stable_dashboard_shell_styles(self) -> None:
        os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
        from PyQt6.QtWidgets import QApplication

        app_instance = QApplication.instance() or QApplication([])
        with tempfile.TemporaryDirectory() as tmpdir:
            app = bootstrap_application(Path(tmpdir))
            window = MainWindow(
                agent=app.agent,
                settings=app.settings,
                document_service=app.document_service,
                llm_service=app.llm_service,
            )

            self.assertGreaterEqual(window.minimumWidth(), 1200)
            self.assertGreaterEqual(window.minimumHeight(), 760)
            self.assertEqual(window.send_button.objectName(), "PrimaryButton")
            self.assertEqual(window.cancel_button.objectName(), "SecondaryButton")
            self.assertEqual(window.retry_button.objectName(), "GhostButton")
            self.assertEqual(window.snapshot_button.objectName(), "GhostButton")
            self.assertEqual(window.demo_state_button.objectName(), "SecondaryButton")
            self.assertIn("QFrame#HeroPanel", window.styleSheet())
            self.assertIn("QFrame#SurfaceCard", window.styleSheet())
            self.assertIn("QLabel {", window.styleSheet())
            self.assertIn("background: transparent;", window.styleSheet())
            app_instance.processEvents()

    def test_main_window_centers_itself_within_available_screen(self) -> None:
        os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
        from PyQt6.QtWidgets import QApplication

        app_instance = QApplication.instance() or QApplication([])
        with tempfile.TemporaryDirectory() as tmpdir:
            app = bootstrap_application(Path(tmpdir))
            window = MainWindow(
                agent=app.agent,
                settings=app.settings,
                document_service=app.document_service,
                llm_service=app.llm_service,
            )

            window.resize(1440, 900)
            window.center_on_screen()
            app_instance.processEvents()

            screen = window.screen() or app_instance.primaryScreen()
            screen_center = screen.availableGeometry().center()
            frame_center = window.frameGeometry().center()

            self.assertLessEqual(abs(frame_center.x() - screen_center.x()), 2)
            self.assertLessEqual(abs(frame_center.y() - screen_center.y()), 2)

    def test_main_window_applies_large_startup_geometry_for_desktop_screen(self) -> None:
        os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
        from PyQt6.QtWidgets import QApplication

        class FakeScreen:
            def availableGeometry(self):
                from PyQt6.QtCore import QRect

                return QRect(0, 0, 1920, 1080)

        app_instance = QApplication.instance() or QApplication([])
        with tempfile.TemporaryDirectory() as tmpdir:
            app = bootstrap_application(Path(tmpdir))
            window = MainWindow(
                agent=app.agent,
                settings=app.settings,
                document_service=app.document_service,
                llm_service=app.llm_service,
            )

            window.apply_startup_geometry(FakeScreen())
            app_instance.processEvents()

            self.assertGreaterEqual(window.width(), 1440)
            self.assertGreaterEqual(window.height(), 880)

    def test_main_window_keeps_right_diagnostics_panel_visible_in_default_layout(self) -> None:
        os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
        from PyQt6.QtWidgets import QApplication

        app_instance = QApplication.instance() or QApplication([])
        with tempfile.TemporaryDirectory() as tmpdir:
            app = bootstrap_application(Path(tmpdir))
            window = MainWindow(
                agent=app.agent,
                settings=app.settings,
                document_service=app.document_service,
                llm_service=app.llm_service,
            )
            window.show()
            app_instance.processEvents()

            sizes = window.workspace_splitter.sizes()

            self.assertEqual(len(sizes), 3)
            self.assertGreater(sizes[2], 260)
            self.assertGreaterEqual(window.workspace_splitter.widget(2).minimumWidth(), 320)
            self.assertTrue(window.side_scroll_area.widgetResizable())

    def test_main_window_renders_compact_knowledge_base_summary_instead_of_full_file_list(self) -> None:
        os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
        from PyQt6.QtWidgets import QApplication

        app_instance = QApplication.instance() or QApplication([])
        with tempfile.TemporaryDirectory() as tmpdir:
            app = bootstrap_application(Path(tmpdir))
            (app.settings.docs_dir / "redis-guide.md").write_text("# Redis\n\n## timeout\n\n检查连接池。", encoding="utf-8")
            (app.settings.docs_dir / "mysql-tuning.md").write_text("# MySQL\n\n## 索引\n\n检查慢查询。", encoding="utf-8")
            IngestPipeline(settings=app.settings, repository=app.repository).ingest_directory(app.settings.docs_dir)
            window = MainWindow(
                agent=app.agent,
                settings=app.settings,
                document_service=app.document_service,
                llm_service=app.llm_service,
            )
            app_instance.processEvents()

            self.assertLessEqual(window.workspace_splitter.widget(0).minimumWidth(), 220)
            self.assertLessEqual(window.docs_summary_panel.maximumHeight(), 280)
            self.assertIn("知识库摘要", window.docs_summary_panel.toPlainText())
            self.assertIn("覆盖领域", window.docs_summary_panel.toPlainText())
            self.assertIn("核心主题", window.docs_summary_panel.toPlainText())
            self.assertIn("Redis", window.docs_summary_panel.toPlainText())
            self.assertIn("MySQL", window.docs_summary_panel.toPlainText())
            self.assertNotIn("redis-guide.md", window.docs_summary_panel.toPlainText())

    def test_main_window_can_load_demo_state_and_export_snapshot(self) -> None:
        os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
        from PyQt6.QtWidgets import QApplication

        app_instance = QApplication.instance() or QApplication([])
        with tempfile.TemporaryDirectory() as tmpdir:
            app = bootstrap_application(Path(tmpdir))
            window = MainWindow(
                agent=app.agent,
                settings=app.settings,
                document_service=app.document_service,
                llm_service=app.llm_service,
            )
            output = Path(tmpdir) / "desktop-demo.png"

            window.load_demo_state()
            window.show()
            app_instance.processEvents()

            exported = window.export_snapshot(output)

            self.assertTrue(exported)
            self.assertTrue(output.exists())
            self.assertGreater(output.stat().st_size, 0)
            self.assertIn("provider=http_429", window.provider_diagnostics_panel.toPlainText())
            self.assertIn("Redis", window.sources_panel.toPlainText())
            self.assertIn("restart_mock_service", window.tool_logs_panel.toPlainText())

    def test_main_window_can_export_current_snapshot_via_helper(self) -> None:
        os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
        from PyQt6.QtWidgets import QApplication

        app_instance = QApplication.instance() or QApplication([])
        with tempfile.TemporaryDirectory() as tmpdir:
            app = bootstrap_application(Path(tmpdir))
            window = MainWindow(
                agent=app.agent,
                settings=app.settings,
                document_service=app.document_service,
                llm_service=app.llm_service,
            )
            output = Path(tmpdir) / "manual-ui-export.png"
            window.show()
            app_instance.processEvents()

            exported = window.export_current_snapshot(output)

            self.assertEqual(exported, output)
            self.assertTrue(output.exists())
            self.assertGreater(output.stat().st_size, 0)

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
            self.assertIn("fallback", window.request_status.text())
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

    def test_main_window_renders_provider_stream_chunks_without_fake_chunk_timer(self) -> None:
        os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
        from PyQt6.QtWidgets import QApplication

        class StreamingChatPage:
            def __init__(self) -> None:
                self.messages = []

            def stream_message(self, content: str):
                self.messages.append({"role": "user", "content": content})
                yield {"type": "delta", "delta": "先检查 Redis 状态，"}
                time.sleep(0.02)
                yield {"type": "delta", "delta": "再查看 timeout 日志。"}
                yield {
                    "type": "done",
                    "response": SimpleNamespace(
                        answer="先检查 Redis 状态，再查看 timeout 日志。",
                        sources=[],
                        tool_logs=[],
                        answer_backend="remote",
                        provider_status="success",
                        provider_diagnostic="provider=success | attempts=1 | first_token=180ms | total=640ms",
                        provider_error="",
                        provider_attempts=1,
                        first_token_latency_ms=180,
                        total_latency_ms=640,
                        retrieval_stage_latency_ms={
                            "retrieval": 42,
                            "coarse_rerank": 8,
                            "bge_rerank": 31,
                            "context_build": 5,
                        },
                    ),
                }

        app_instance = QApplication.instance() or QApplication([])
        with tempfile.TemporaryDirectory() as tmpdir:
            app = bootstrap_application(Path(tmpdir))
            window = MainWindow(
                agent=app.agent,
                settings=app.settings,
                document_service=app.document_service,
                llm_service=app.llm_service,
            )
            window.chat_page = StreamingChatPage()
            window._stream_chunk_size = 100

            window.input_box.setPlainText("Redis timeout 怎么排查？")
            window.handle_send()

            deadline = time.monotonic() + 2.0
            saw_partial = False
            while time.monotonic() < deadline:
                app_instance.processEvents()
                time.sleep(0.02)
                text = window.chat_history.toPlainText()
                if "先检查 Redis 状态，" in text and "timeout 日志。" not in text:
                    saw_partial = True
                    break

            self.assertTrue(saw_partial)
            self.assertIn("stream", window.request_status.text())

            deadline = time.monotonic() + 2.0
            while "timeout 日志。" not in window.chat_history.toPlainText():
                if time.monotonic() > deadline:
                    self.fail("Timed out waiting for provider stream to finish.")
                app_instance.processEvents()
                time.sleep(0.02)

            self.assertIn("remote", window.request_status.text())
            self.assertIn("状态：已完成", window.request_status.text())
            self.assertIn("首包延迟：180 ms", window.provider_metrics_panel.toPlainText())
            self.assertIn("总耗时：640 ms", window.provider_metrics_panel.toPlainText())
            self.assertIn("provider=success", window.provider_diagnostics_panel.toPlainText())
            self.assertIn("检索：42 ms", window.retrieval_stage_panel.toPlainText())
            self.assertIn("粗排：8 ms", window.retrieval_stage_panel.toPlainText())
            self.assertIn("BGE：31 ms", window.retrieval_stage_panel.toPlainText())
            self.assertIn("上下文构造：5 ms", window.retrieval_stage_panel.toPlainText())

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

    def test_main_window_marks_remote_answer_source_in_status(self) -> None:
        os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
        from PyQt6.QtWidgets import QApplication

        class RemoteChatPage:
            def __init__(self) -> None:
                self.messages = []

            def send_message(self, content: str):
                self.messages.append({"role": "user", "content": content})
                return SimpleNamespace(
                    answer="这是远程模型的回答。",
                    sources=[],
                    tool_logs=[],
                    answer_backend="remote",
                    provider_status="success",
                    provider_error="",
                    provider_attempts=1,
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
            window.chat_page = RemoteChatPage()
            window._stream_chunk_size = 100

            window.input_box.setPlainText("测试远程回答来源")
            window.handle_send()

            deadline = time.monotonic() + 2.0
            while "这是远程模型的回答" not in window.chat_history.toPlainText():
                if time.monotonic() > deadline:
                    self.fail("Timed out waiting for remote answer label.")
                app_instance.processEvents()
                time.sleep(0.02)

            self.assertIn("remote", window.request_status.text())
            self.assertIn("success", window.request_status.text())

    def test_main_window_marks_provider_failure_diagnostics_in_status(self) -> None:
        os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
        from PyQt6.QtWidgets import QApplication

        class FallbackChatPage:
            def __init__(self) -> None:
                self.messages = []

            def send_message(self, content: str):
                self.messages.append({"role": "user", "content": content})
                return SimpleNamespace(
                    answer="这是 fallback 回答。",
                    sources=[],
                    tool_logs=[],
                    answer_backend="fallback",
                    provider_status="timeout",
                    provider_diagnostic="provider=timeout | attempts=2 | total=1800ms | error=timed out",
                    provider_error="timed out",
                    provider_attempts=2,
                    first_token_latency_ms=0,
                    total_latency_ms=1800,
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
            window.chat_page = FallbackChatPage()
            window._stream_chunk_size = 100

            window.input_box.setPlainText("测试 provider 失败诊断")
            window.handle_send()

            deadline = time.monotonic() + 2.0
            while "这是 fallback 回答" not in window.chat_history.toPlainText():
                if time.monotonic() > deadline:
                    self.fail("Timed out waiting for provider diagnostics label.")
                app_instance.processEvents()
                time.sleep(0.02)

            self.assertIn("fallback", window.request_status.text())
            self.assertIn("timeout", window.request_status.text())
            self.assertIn("attempts=2", window.request_status.text())
            self.assertIn("总耗时：1800 ms", window.provider_metrics_panel.toPlainText())
            self.assertIn("timed out", window.provider_diagnostics_panel.toPlainText())

    def test_main_window_shows_live_first_token_timing_during_provider_stream(self) -> None:
        os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
        from PyQt6.QtWidgets import QApplication

        class StreamingChatPage:
            def __init__(self) -> None:
                self.messages = []

            def stream_message(self, content: str):
                self.messages.append({"role": "user", "content": content})
                yield {"type": "delta", "delta": "先检查 Redis 状态，"}
                time.sleep(0.02)
                yield {"type": "delta", "delta": "再查看 timeout 日志。"}
                yield {
                    "type": "done",
                    "response": SimpleNamespace(
                        answer="先检查 Redis 状态，再查看 timeout 日志。",
                        sources=[],
                        tool_logs=[],
                        answer_backend="remote",
                        provider_status="success",
                        provider_diagnostic="provider=success | attempts=1 | first_token=55ms | total=420ms",
                        provider_error="",
                        provider_attempts=1,
                        first_token_latency_ms=55,
                        total_latency_ms=420,
                    ),
                }

        app_instance = QApplication.instance() or QApplication([])
        with tempfile.TemporaryDirectory() as tmpdir:
            app = bootstrap_application(Path(tmpdir))
            window = MainWindow(
                agent=app.agent,
                settings=app.settings,
                document_service=app.document_service,
                llm_service=app.llm_service,
            )
            window.chat_page = StreamingChatPage()
            window._stream_interval_ms = 10

            window.input_box.setPlainText("Redis timeout 怎么排查？")
            started_at = time.monotonic()
            window.handle_send()

            deadline = time.monotonic() + 2.0
            while time.monotonic() < deadline:
                app_instance.processEvents()
                time.sleep(0.01)
                if "首包延迟：" in window.provider_metrics_panel.toPlainText():
                    break

            self.assertIn("首包延迟：", window.provider_metrics_panel.toPlainText())
            elapsed_ms = (time.monotonic() - started_at) * 1000
            self.assertLess(elapsed_ms, 250)

            deadline = time.monotonic() + 2.0
            while "timeout 日志。" not in window.chat_history.toPlainText():
                if time.monotonic() > deadline:
                    self.fail("Timed out waiting for provider stream completion after first-token telemetry.")
                app_instance.processEvents()
                time.sleep(0.01)

    def test_main_window_displays_current_session_summary(self) -> None:
        os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
        from PyQt6.QtWidgets import QApplication

        class SummaryChatPage:
            def __init__(self) -> None:
                self.messages = []

            def send_message(self, content: str):
                self.messages.append({"role": "user", "content": content})
                return SimpleNamespace(
                    answer="建议先检查 Redis maxmemory 和 slowlog。",
                    sources=[],
                    tool_logs=[],
                    summary="本轮问题：Redis OOM 怎么排查；最新结论：检查 maxmemory 和 slowlog。",
                    answer_backend="fallback",
                    provider_status="not_used",
                    provider_error="",
                    provider_attempts=0,
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
            window.chat_page = SummaryChatPage()
            window._stream_chunk_size = 100

            window.input_box.setPlainText("Redis OOM 怎么排查？")
            window.handle_send()

            deadline = time.monotonic() + 2.0
            while "maxmemory" not in window.chat_history.toPlainText():
                if time.monotonic() > deadline:
                    self.fail("Timed out waiting for answer before checking summary.")
                app_instance.processEvents()
                time.sleep(0.02)

            self.assertIn("当前会话摘要", window.session_summary_panel.toPlainText())
            self.assertIn("Redis OOM", window.session_summary_panel.toPlainText())
            self.assertIn("slowlog", window.session_summary_panel.toPlainText())

    def test_main_window_displays_retrieval_and_embedding_backends(self) -> None:
        os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
        from PyQt6.QtWidgets import QApplication

        class BackendChatPage:
            def __init__(self) -> None:
                self.messages = []

            def send_message(self, content: str):
                self.messages.append({"role": "user", "content": content})
                return SimpleNamespace(
                    answer="检索已完成。",
                    sources=[],
                    tool_logs=[],
                    summary="暂无摘要。",
                    answer_backend="fallback",
                    provider_status="not_used",
                    provider_error="",
                    provider_attempts=0,
                    retrieval_backend="remote",
                    embedding_backend="hash",
                    reranker_backend="bge",
                    node_trace=["intent", "retrieve", "plan", "answer"],
                    plan_route="answer",
                    recovery_action="retry_repaired_action",
                    tool_actions=[
                        {"tool_name": "check_service_status", "tool_input": {"service_name": "redis"}},
                        {"tool_name": "search_error_logs", "tool_input": {"keyword": "timeout"}},
                    ],
                )

        app_instance = QApplication.instance() or QApplication([])
        with tempfile.TemporaryDirectory() as tmpdir:
            app = bootstrap_application(Path(tmpdir))
            settings = SimpleNamespace(**vars(app.settings))
            settings.retrieval_backend = "remote"
            settings.embedding_backend = "hash"
            settings.reranker_backend = "bge"
            window = MainWindow(
                agent=app.agent,
                settings=settings,
                document_service=app.document_service,
                llm_service=app.llm_service,
            )
            window.chat_page = BackendChatPage()
            window._stream_chunk_size = 100

            self.assertIn("Retrieval 后端：remote", window.retrieval_status.text())
            self.assertIn("Embedding 后端：hash", window.embedding_status.text())
            self.assertIn("Reranker 后端：bge", window.reranker_status.text())

            window.input_box.setPlainText("测试检索后端展示")
            window.handle_send()

            deadline = time.monotonic() + 2.0
            while "检索已完成" not in window.chat_history.toPlainText():
                if time.monotonic() > deadline:
                    self.fail("Timed out waiting for backend metadata response.")
                app_instance.processEvents()
                time.sleep(0.02)

            self.assertIn("retrieval=remote", window.request_status.text())
            self.assertIn("embedding=hash", window.request_status.text())
            self.assertIn("reranker=bge", window.request_status.text())
            self.assertIn("plan=answer", window.request_status.text())
            self.assertIn("trace=intent>retrieve>plan>answer", window.request_status.text())
            self.assertIn("actions=2", window.request_status.text())
            self.assertIn("tools=check_service_status,search_error_logs", window.request_status.text())
            self.assertIn("recovery=retry_repaired_action", window.request_status.text())


if __name__ == "__main__":
    unittest.main()
