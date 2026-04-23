import os
import tempfile
import unittest
from pathlib import Path

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

            self.assertIn("请重启 redis 服务", window.chat_history.toPlainText())
            self.assertIn("已执行模拟工具", window.chat_history.toPlainText())
            self.assertIn("Redis", window.sources_panel.toPlainText())
            self.assertIn("restart_mock_service", window.tool_logs_panel.toPlainText())
            app_instance.processEvents()


if __name__ == "__main__":
    unittest.main()
