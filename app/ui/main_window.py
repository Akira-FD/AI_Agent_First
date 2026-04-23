from __future__ import annotations

from dataclasses import dataclass

from app.ui.pages.chat_page import ChatPage
from app.ui.pages.docs_page import DocsPage
from app.ui.pages.logs_page import LogsPage
from app.ui.widgets.source_card import SourceCard
from app.ui.widgets.tool_log_panel import ToolLogPanel

try:
    from PyQt6.QtCore import QObject, QThread, QTimer, Qt, pyqtSignal
    from PyQt6.QtGui import QTextCursor
    from PyQt6.QtWidgets import (
        QApplication,
        QHBoxLayout,
        QLabel,
        QListWidget,
        QMainWindow,
        QPushButton,
        QSplitter,
        QTextBrowser,
        QTextEdit,
        QVBoxLayout,
        QWidget,
    )
except ModuleNotFoundError:
    QApplication = None
    QLabel = None
    QObject = object
    QHBoxLayout = None
    QListWidget = None
    QMainWindow = object
    QThread = None
    QTimer = None
    QPushButton = None
    QSplitter = None
    QTextBrowser = None
    QTextCursor = None
    QTextEdit = None
    QVBoxLayout = None
    QWidget = None
    Qt = None
    pyqtSignal = None


if pyqtSignal is not None:
    class _AsyncRequestWorker(QObject):
        finished = pyqtSignal(object)
        failed = pyqtSignal(str)

        def __init__(self, chat_page, query: str) -> None:
            super().__init__()
            self.chat_page = chat_page
            self.query = query

        def run(self) -> None:
            try:
                response = self.chat_page.send_message(self.query)
            except Exception as exc:  # pragma: no cover - exercised through signal handling
                self.failed.emit(str(exc))
                return
            self.finished.emit(response)
else:
    class _AsyncRequestWorker:
        def __init__(self, chat_page, query: str) -> None:
            self.chat_page = chat_page
            self.query = query


@dataclass
class DesktopAppShell:
    agent: object
    settings: object
    document_service: object | None = None
    llm_service: object | None = None

    def render_status(self) -> str:
        backend = describe_llm_backend(self.settings, self.llm_service)
        return (
            f"{self.settings.app_name} MVP shell is ready.\n"
            f"Docs directory: {self.settings.docs_dir}\n"
            f"LLM backend: {backend}\n"
            "UI scaffold: sessions | chat | sources | tool logs"
        )

    def create_pages(self) -> dict[str, object]:
        return {
            "chat": ChatPage(agent=self.agent),
            "docs": DocsPage(document_service=self.document_service),
            "logs": LogsPage(),
        }


def launch_pyqt_app(agent, settings, document_service=None, llm_service=None) -> int:
    if QApplication is None:
        raise RuntimeError("PyQt6 is not installed. Run `pip install PyQt6` before launching the desktop UI.")

    app = QApplication.instance() or QApplication([])
    window = MainWindow(agent=agent, settings=settings, document_service=document_service, llm_service=llm_service)
    window.resize(980, 680)
    window.show()
    return app.exec()


def describe_llm_backend(settings, llm_service) -> str:
    backend = "unknown"
    if llm_service and hasattr(llm_service, "backend_label"):
        backend = llm_service.backend_label()

    llm_api_key = getattr(settings, "llm_api_key", "")
    llm_model = getattr(settings, "llm_model", "")
    llm_base_url = getattr(settings, "llm_base_url", "")

    if backend == "local-rule-based-fallback" and llm_model and llm_base_url and not llm_api_key:
        return f"{backend} (AI_AGENT_FIRST_LLM_API_KEY/OPENAI_API_KEY missing; configured model={llm_model})"
    return backend


class MainWindow(QMainWindow):
    def __init__(self, agent, settings, document_service=None, llm_service=None) -> None:
        super().__init__()
        if QApplication is None:
            raise RuntimeError("PyQt6 is not installed. Run `pip install PyQt6` before launching the desktop UI.")
        self.agent = agent
        self.settings = settings
        self.document_service = document_service
        self.llm_service = llm_service
        self.chat_page = ChatPage(agent=agent, session_id="desktop")
        self.docs_page = DocsPage(document_service=document_service)
        self.tool_log_panel = ToolLogPanel()
        self._request_thread = None
        self._request_worker = None
        self._request_timer = QTimer(self)
        self._request_timer.setSingleShot(True)
        self._request_timer.timeout.connect(self._handle_request_timeout)
        self._stream_timer = QTimer(self)
        self._stream_timer.timeout.connect(self._stream_next_chunk)
        self._request_timeout_ms = max(1000, int(getattr(settings, "llm_timeout_seconds", 30) * 1000))
        self._stream_interval_ms = 24
        self._stream_chunk_size = 18
        self._pending_stream_text = ""
        self._pending_stream_response = None
        self._ignore_current_response = False
        self._pending_retry_query = None
        self._last_query = ""

        self.setWindowTitle(settings.app_name)
        self._build_layout()
        self.refresh_documents()

    def _build_layout(self) -> None:
        root = QWidget()
        root_layout = QVBoxLayout(root)
        header = QLabel(f"{self.settings.app_name} | 本地 MVP 演示")
        header.setStyleSheet("font-size: 18px; font-weight: 700; padding: 8px;")
        root_layout.addWidget(header)
        backend = describe_llm_backend(self.settings, self.llm_service)
        self.backend_status = QLabel(f"LLM 后端：{backend}")
        self.backend_status.setStyleSheet("font-size: 12px; color: #4b5563; padding: 0 8px 8px 8px;")
        root_layout.addWidget(self.backend_status)
        self.request_status = QLabel("状态：空闲")
        self.request_status.setStyleSheet("font-size: 12px; color: #4b5563; padding: 0 8px 8px 8px;")
        root_layout.addWidget(self.request_status)

        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.addWidget(self._build_docs_panel())
        splitter.addWidget(self._build_chat_panel())
        splitter.addWidget(self._build_side_panel())
        splitter.setSizes([220, 520, 300])
        root_layout.addWidget(splitter)
        self.setCentralWidget(root)

    def _build_docs_panel(self):
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.addWidget(QLabel("知识库文档"))
        self.docs_list = QListWidget()
        layout.addWidget(self.docs_list)
        refresh_button = QPushButton("刷新文档")
        refresh_button.clicked.connect(self.refresh_documents)
        layout.addWidget(refresh_button)
        return panel

    def _build_chat_panel(self):
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.addWidget(QLabel("对话"))
        self.chat_history = QTextBrowser()
        layout.addWidget(self.chat_history)

        input_layout = QHBoxLayout()
        self.input_box = QTextEdit()
        self.input_box.setPlaceholderText("输入问题，例如：请重启 redis 服务")
        self.input_box.setFixedHeight(72)
        self.send_button = QPushButton("发送")
        self.send_button.clicked.connect(self.handle_send)
        self.cancel_button = QPushButton("取消")
        self.cancel_button.setEnabled(False)
        self.cancel_button.clicked.connect(self.cancel_current_request)
        self.retry_button = QPushButton("重试")
        self.retry_button.setEnabled(False)
        self.retry_button.clicked.connect(self.retry_last_query)
        input_layout.addWidget(self.input_box)
        input_layout.addWidget(self.send_button)
        input_layout.addWidget(self.cancel_button)
        input_layout.addWidget(self.retry_button)
        layout.addLayout(input_layout)
        return panel

    def _build_side_panel(self):
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.addWidget(QLabel("来源引用"))
        self.sources_panel = QTextBrowser()
        layout.addWidget(self.sources_panel)
        layout.addWidget(QLabel("工具日志"))
        self.tool_logs_panel = QTextBrowser()
        layout.addWidget(self.tool_logs_panel)
        return panel

    def refresh_documents(self) -> None:
        self.docs_list.clear()
        for document in self.docs_page.refresh():
            self.docs_list.addItem(f"{document['source']} | chunks: {document['chunk_count']}")

    def handle_send(self) -> None:
        query = self.input_box.toPlainText().strip()
        if not query:
            return
        if self._request_thread is not None:
            self.request_status.setText("状态：处理中，请等待当前请求完成")
            return
        self.input_box.clear()
        self._start_request(query)

    def _start_request(self, query: str) -> None:
        self._last_query = query
        self._ignore_current_response = False
        self._pending_retry_query = None
        self._pending_stream_text = ""
        self._pending_stream_response = None
        self.chat_history.append(f"用户：{query}")
        self._set_controls(send_enabled=False, cancel_enabled=True, retry_enabled=False)
        self.request_status.setText("状态：处理中...")
        self._request_timer.start(self._request_timeout_ms)

        thread = QThread()
        worker = _AsyncRequestWorker(self.chat_page, query)
        worker.moveToThread(thread)
        thread.started.connect(worker.run)
        worker.finished.connect(self._handle_async_response)
        worker.failed.connect(self._handle_async_error)
        worker.finished.connect(thread.quit)
        worker.failed.connect(thread.quit)
        thread.finished.connect(self._cleanup_request_worker)
        thread.start()

        self._request_thread = thread
        self._request_worker = worker

    def _handle_async_response(self, response) -> None:
        self._request_timer.stop()
        if self._ignore_current_response:
            return
        self._pending_stream_response = response
        self._pending_stream_text = response.answer or ""
        self._render_response_metadata(response)
        self.chat_history.append("助手：")
        if not self._pending_stream_text:
            self._finish_streaming_response()
            return
        self.request_status.setText("状态：输出中...")
        self._set_controls(send_enabled=False, cancel_enabled=True, retry_enabled=False)
        self._stream_timer.start(self._stream_interval_ms)

    def _handle_async_error(self, error_message: str) -> None:
        self._request_timer.stop()
        self.chat_history.append(f"助手：请求失败，{error_message}")
        self.request_status.setText("状态：请求失败，可重试")
        self._set_controls(send_enabled=True, cancel_enabled=False, retry_enabled=bool(self._last_query))

    def _cleanup_request_worker(self) -> None:
        if self._request_worker is not None and hasattr(self._request_worker, "deleteLater"):
            self._request_worker.deleteLater()
        if self._request_thread is not None:
            self._request_thread.deleteLater()
        self._request_worker = None
        self._request_thread = None
        if self._pending_retry_query:
            retry_query = self._pending_retry_query
            self._pending_retry_query = None
            self._start_request(retry_query)
            return
        if self._ignore_current_response and not self._stream_timer.isActive():
            self._set_controls(send_enabled=True, cancel_enabled=False, retry_enabled=bool(self._last_query))

    def _stream_next_chunk(self) -> None:
        if not self._pending_stream_text:
            self._finish_streaming_response()
            return
        next_chunk = self._pending_stream_text[: self._stream_chunk_size]
        self._pending_stream_text = self._pending_stream_text[self._stream_chunk_size :]
        cursor = self.chat_history.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        self.chat_history.setTextCursor(cursor)
        self.chat_history.insertPlainText(next_chunk)
        if not self._pending_stream_text:
            self._finish_streaming_response()

    def _finish_streaming_response(self) -> None:
        self._stream_timer.stop()
        response = self._pending_stream_response
        self._pending_stream_response = None
        self._pending_stream_text = ""
        if self._ignore_current_response or response is None:
            self.request_status.setText("状态：已取消")
            self._set_controls(send_enabled=True, cancel_enabled=False, retry_enabled=bool(self._last_query))
            return

        self.chat_history.append("")
        self.request_status.setText("状态：已完成")
        self._set_controls(send_enabled=True, cancel_enabled=False, retry_enabled=bool(self._last_query))

    def _handle_request_timeout(self) -> None:
        if self._request_thread is None:
            return
        self._ignore_current_response = True
        self.request_status.setText("状态：请求超时，可重试")
        self._set_controls(send_enabled=False, cancel_enabled=True, retry_enabled=bool(self._last_query))

    def cancel_current_request(self) -> None:
        if self._request_thread is None and not self._stream_timer.isActive():
            return
        self._request_timer.stop()
        self._ignore_current_response = True
        if self._stream_timer.isActive():
            self._finish_streaming_response()
            return
        self.request_status.setText("状态：已取消")
        self._set_controls(send_enabled=False, cancel_enabled=False, retry_enabled=bool(self._last_query))

    def retry_last_query(self) -> None:
        if not self._last_query:
            return
        if self._request_thread is not None:
            self._pending_retry_query = self._last_query
            self._ignore_current_response = True
            self.request_status.setText("状态：当前请求结束后自动重试")
            self._set_controls(send_enabled=False, cancel_enabled=True, retry_enabled=False)
            return
        if self._stream_timer.isActive():
            self.cancel_current_request()
            self._pending_retry_query = self._last_query
            return
        self._start_request(self._last_query)

    def _set_controls(self, *, send_enabled: bool, cancel_enabled: bool, retry_enabled: bool) -> None:
        self.send_button.setEnabled(send_enabled)
        self.cancel_button.setEnabled(cancel_enabled)
        self.retry_button.setEnabled(retry_enabled)

    def _render_response_metadata(self, response) -> None:
        self.sources_panel.clear()
        for source in response.sources:
            self.sources_panel.append(SourceCard(source).render_text())
            self.sources_panel.append("")

        self.tool_log_panel = ToolLogPanel()
        self.tool_logs_panel.clear()
        for log in response.tool_logs:
            self.tool_log_panel.add_log(log)
        self.tool_logs_panel.setPlainText(self.tool_log_panel.render_text())
