from __future__ import annotations

from dataclasses import dataclass
import time

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
        streamed = pyqtSignal(str)
        stream_completed = pyqtSignal(object)

        def __init__(self, chat_page, query: str) -> None:
            super().__init__()
            self.chat_page = chat_page
            self.query = query

        def run(self) -> None:
            try:
                if hasattr(self.chat_page, "stream_message"):
                    for event in self.chat_page.stream_message(self.query):
                        if event.get("type") == "delta":
                            self.streamed.emit(str(event.get("delta", "")))
                        elif event.get("type") == "done":
                            self.stream_completed.emit(event.get("response"))
                    return
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
    window.resize(1180, 760)
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


def describe_retrieval_backend(settings) -> str:
    return getattr(settings, "retrieval_backend", "unknown")


def describe_embedding_backend(settings) -> str:
    return getattr(settings, "embedding_backend", "unknown")


def describe_reranker_backend(settings) -> str:
    return getattr(settings, "reranker_backend", "unknown")


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
        self._provider_stream_timer = QTimer(self)
        self._provider_stream_timer.timeout.connect(self._flush_provider_stream_delta)
        self._request_timeout_ms = max(1000, int(getattr(settings, "llm_timeout_seconds", 30) * 1000))
        self._stream_interval_ms = 24
        self._stream_chunk_size = 18
        self._pending_stream_text = ""
        self._pending_stream_response = None
        self._pending_provider_deltas: list[str] = []
        self._pending_provider_completed_response = None
        self._streaming_from_provider = False
        self._pending_answer_backend = "unknown"
        self._pending_provider_status = "not_used"
        self._pending_provider_error = ""
        self._pending_provider_attempts = 0
        self._pending_plan_steps = []
        self._pending_replan_steps = []
        self._pending_first_token_latency_ms = 0
        self._pending_total_latency_ms = 0
        self._pending_provider_diagnostic = ""
        self._pending_retrieval_stage_latency_ms = {}
        self._ignore_current_response = False
        self._pending_retry_query = None
        self._last_query = ""
        self._request_started_at = 0.0
        self._first_visible_token_recorded = False

        self.setWindowTitle(settings.app_name)
        self._apply_theme()
        self._build_layout()
        self.refresh_documents()

    def _apply_theme(self) -> None:
        self.setStyleSheet(
            """
            QMainWindow, QWidget {
                background: #f5f7fb;
                color: #14213d;
                font-family: "Segoe UI", "Microsoft YaHei";
            }
            QLabel {
                color: #33415c;
            }
            QListWidget, QTextBrowser, QTextEdit {
                background: #ffffff;
                border: 1px solid #d9e2f2;
                border-radius: 12px;
                padding: 8px;
                selection-background-color: #dbeafe;
            }
            QPushButton {
                background: #0f766e;
                color: white;
                border: none;
                border-radius: 10px;
                padding: 10px 14px;
                font-weight: 600;
            }
            QPushButton:disabled {
                background: #b8c4d6;
                color: #eef2f7;
            }
            QPushButton:hover:!disabled {
                background: #115e59;
            }
            """
        )

    def _build_layout(self) -> None:
        root = QWidget()
        root_layout = QVBoxLayout(root)
        header = QLabel(f"{self.settings.app_name} | 桌面端智能助理")
        header.setStyleSheet("font-size: 24px; font-weight: 700; padding: 6px 8px 0 8px; color: #0f172a;")
        root_layout.addWidget(header)
        subheader = QLabel("RAG 检索、Agent 执行、LLM 回答与会话摘要的统一工作台")
        subheader.setStyleSheet("font-size: 13px; color: #64748b; padding: 0 8px 10px 8px;")
        root_layout.addWidget(subheader)
        backend = describe_llm_backend(self.settings, self.llm_service)
        self.backend_status = QLabel(f"LLM 后端：{backend}")
        self.backend_status.setStyleSheet("font-size: 12px; color: #334155; padding: 4px 10px; background: #e2f3ff; border-radius: 8px;")
        root_layout.addWidget(self.backend_status)
        self.retrieval_status = QLabel(f"Retrieval 后端：{describe_retrieval_backend(self.settings)}")
        self.retrieval_status.setStyleSheet("font-size: 12px; color: #334155; padding: 4px 10px; background: #eef6e8; border-radius: 8px;")
        root_layout.addWidget(self.retrieval_status)
        self.embedding_status = QLabel(f"Embedding 后端：{describe_embedding_backend(self.settings)}")
        self.embedding_status.setStyleSheet("font-size: 12px; color: #334155; padding: 4px 10px; background: #fff6dd; border-radius: 8px;")
        root_layout.addWidget(self.embedding_status)
        self.reranker_status = QLabel(f"Reranker 后端：{describe_reranker_backend(self.settings)}")
        self.reranker_status.setStyleSheet("font-size: 12px; color: #334155; padding: 4px 10px; background: #fce7f3; border-radius: 8px;")
        root_layout.addWidget(self.reranker_status)
        self.request_status = QLabel("状态：空闲")
        self.request_status.setStyleSheet("font-size: 12px; color: #334155; padding: 8px 10px; background: #ffffff; border: 1px solid #d9e2f2; border-radius: 10px;")
        root_layout.addWidget(self.request_status)

        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.addWidget(self._build_docs_panel())
        splitter.addWidget(self._build_chat_panel())
        splitter.addWidget(self._build_side_panel())
        splitter.setSizes([250, 610, 320])
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
        self.input_box.setPlaceholderText("输入问题，例如：请先查询 redis 状态，再查一下 timeout 日志，最后给我总结根因")
        self.input_box.setFixedHeight(90)
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
        layout.addWidget(QLabel("请求指标"))
        self.provider_metrics_panel = QTextBrowser()
        self.provider_metrics_panel.setMaximumHeight(90)
        self.provider_metrics_panel.setPlainText("首包延迟：暂无\n总耗时：暂无")
        layout.addWidget(self.provider_metrics_panel)
        layout.addWidget(QLabel("Provider 诊断"))
        self.provider_diagnostics_panel = QTextBrowser()
        self.provider_diagnostics_panel.setMaximumHeight(110)
        self.provider_diagnostics_panel.setPlainText("暂无 provider 诊断")
        layout.addWidget(self.provider_diagnostics_panel)
        layout.addWidget(QLabel("RAG 阶段耗时"))
        self.retrieval_stage_panel = QTextBrowser()
        self.retrieval_stage_panel.setMaximumHeight(120)
        self.retrieval_stage_panel.setPlainText("检索：暂无\n粗排：暂无\nBGE：暂无\n上下文构造：暂无")
        layout.addWidget(self.retrieval_stage_panel)
        layout.addWidget(QLabel("当前会话摘要"))
        self.session_summary_panel = QTextBrowser()
        self.session_summary_panel.setPlainText("当前会话摘要：暂无")
        self.session_summary_panel.setMaximumHeight(150)
        layout.addWidget(self.session_summary_panel)
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
        self._pending_provider_deltas = []
        self._pending_provider_completed_response = None
        self._streaming_from_provider = False
        self._pending_answer_backend = "unknown"
        self._pending_provider_status = "not_used"
        self._pending_provider_error = ""
        self._pending_provider_attempts = 0
        self._pending_first_token_latency_ms = 0
        self._pending_total_latency_ms = 0
        self._pending_provider_diagnostic = ""
        self._pending_retrieval_stage_latency_ms = {}
        self._pending_plan_steps = []
        self._pending_replan_steps = []
        self._request_started_at = time.monotonic()
        self._first_visible_token_recorded = False
        self.chat_history.append(f"用户：{query}")
        self._set_controls(send_enabled=False, cancel_enabled=True, retry_enabled=False)
        self.request_status.setText("状态：处理中...")
        self.provider_metrics_panel.setPlainText("首包延迟：测量中...\n总耗时：进行中...")
        self.provider_diagnostics_panel.setPlainText("provider=processing")
        self.retrieval_stage_panel.setPlainText("检索：测量中...\n粗排：待执行\nBGE：待执行\n上下文构造：待执行")
        self._request_timer.start(self._request_timeout_ms)

        thread = QThread()
        worker = _AsyncRequestWorker(self.chat_page, query)
        worker.moveToThread(thread)
        thread.started.connect(worker.run)
        worker.finished.connect(self._handle_async_response)
        worker.streamed.connect(self._handle_stream_delta)
        worker.stream_completed.connect(self._handle_stream_completed)
        worker.failed.connect(self._handle_async_error)
        worker.finished.connect(thread.quit)
        worker.stream_completed.connect(thread.quit)
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
        self._pending_answer_backend = getattr(response, "answer_backend", "unknown")
        self._pending_provider_status = getattr(response, "provider_status", "not_used")
        self._pending_provider_error = getattr(response, "provider_error", "")
        self._pending_provider_attempts = getattr(response, "provider_attempts", 0)
        self._pending_first_token_latency_ms = getattr(response, "first_token_latency_ms", 0)
        self._pending_total_latency_ms = getattr(response, "total_latency_ms", 0)
        self._pending_provider_diagnostic = getattr(response, "provider_diagnostic", "")
        self._pending_retrieval_stage_latency_ms = dict(getattr(response, "retrieval_stage_latency_ms", {}) or {})
        self._pending_retrieval_backend = getattr(response, "retrieval_backend", describe_retrieval_backend(self.settings))
        self._pending_embedding_backend = getattr(response, "embedding_backend", describe_embedding_backend(self.settings))
        self._pending_reranker_backend = getattr(response, "reranker_backend", describe_reranker_backend(self.settings))
        self._pending_plan_route = getattr(response, "plan_route", "")
        self._pending_plan_steps = list(getattr(response, "plan_steps", []))
        self._pending_node_trace = list(getattr(response, "node_trace", []))
        self._pending_tool_actions = list(getattr(response, "tool_actions", []))
        self._pending_recovery_action = getattr(response, "recovery_action", "")
        self._pending_replan_steps = list(getattr(response, "replan_steps", []))
        self._render_response_metadata(response)
        self.chat_history.append("助手：")
        if not self._pending_stream_text:
            self._finish_streaming_response()
            return
        self.request_status.setText(
            f"状态：输出中... | 回答来源：{self._pending_answer_backend} | "
            f"provider={self._pending_provider_status} | attempts={self._pending_provider_attempts}"
        )
        self._set_controls(send_enabled=False, cancel_enabled=True, retry_enabled=False)
        self._append_stream_chunk()
        if self._pending_stream_text:
            self._stream_timer.start(self._stream_interval_ms)

    def _handle_stream_delta(self, delta: str) -> None:
        self._request_timer.stop()
        if self._ignore_current_response:
            return
        if not self._streaming_from_provider:
            self._streaming_from_provider = True
            self.chat_history.append("助手：")
            self.request_status.setText("状态：SSE 输出中... | stream=provider")
            self._set_controls(send_enabled=False, cancel_enabled=True, retry_enabled=False)
        if not delta:
            return
        self._pending_provider_deltas.append(delta)
        if len(self._pending_provider_deltas) == 1 and not self._provider_stream_timer.isActive():
            self._flush_provider_stream_delta()
            if self._request_thread is not None and not self._provider_stream_timer.isActive():
                self._provider_stream_timer.start(self._stream_interval_ms)
        elif not self._provider_stream_timer.isActive():
            self._provider_stream_timer.start(self._stream_interval_ms)

    def _handle_stream_completed(self, response) -> None:
        self._request_timer.stop()
        if self._ignore_current_response:
            return
        if not self._streaming_from_provider:
            self._handle_async_response(response)
            return
        if self._pending_provider_deltas or self._provider_stream_timer.isActive():
            self._pending_provider_completed_response = response
            return
        self._finalize_provider_stream(response)

    def _finalize_provider_stream(self, response) -> None:
        self._pending_stream_response = response
        self._pending_answer_backend = getattr(response, "answer_backend", "unknown")
        self._pending_provider_status = getattr(response, "provider_status", "not_used")
        self._pending_provider_error = getattr(response, "provider_error", "")
        self._pending_provider_attempts = getattr(response, "provider_attempts", 0)
        self._pending_first_token_latency_ms = getattr(response, "first_token_latency_ms", 0)
        self._pending_total_latency_ms = getattr(response, "total_latency_ms", 0)
        self._pending_provider_diagnostic = getattr(response, "provider_diagnostic", "")
        self._pending_retrieval_stage_latency_ms = dict(getattr(response, "retrieval_stage_latency_ms", {}) or {})
        self._pending_retrieval_backend = getattr(response, "retrieval_backend", describe_retrieval_backend(self.settings))
        self._pending_embedding_backend = getattr(response, "embedding_backend", describe_embedding_backend(self.settings))
        self._pending_reranker_backend = getattr(response, "reranker_backend", describe_reranker_backend(self.settings))
        self._pending_plan_route = getattr(response, "plan_route", "")
        self._pending_plan_steps = list(getattr(response, "plan_steps", []))
        self._pending_node_trace = list(getattr(response, "node_trace", []))
        self._pending_tool_actions = list(getattr(response, "tool_actions", []))
        self._pending_recovery_action = getattr(response, "recovery_action", "")
        self._pending_replan_steps = list(getattr(response, "replan_steps", []))
        self._render_response_metadata(response)
        self._finish_streaming_response()

    def _flush_provider_stream_delta(self) -> None:
        if self._ignore_current_response:
            self._provider_stream_timer.stop()
            self._pending_provider_deltas = []
            self._pending_provider_completed_response = None
            return
        if not self._pending_provider_deltas:
            self._provider_stream_timer.stop()
            if self._pending_provider_completed_response is not None:
                response = self._pending_provider_completed_response
                self._pending_provider_completed_response = None
                self._finalize_provider_stream(response)
            return
        next_delta = self._pending_provider_deltas.pop(0)
        self._append_chat_text(next_delta)
        if not self._pending_provider_deltas:
            self._provider_stream_timer.stop()
            if self._pending_provider_completed_response is not None:
                response = self._pending_provider_completed_response
                self._pending_provider_completed_response = None
                self._finalize_provider_stream(response)

    def _handle_async_error(self, error_message: str) -> None:
        self._request_timer.stop()
        self.chat_history.append(f"助手：请求失败，{error_message}")
        self.request_status.setText("状态：请求失败，可重试")
        self.provider_metrics_panel.setPlainText("首包延迟：失败\n总耗时：失败")
        self.provider_diagnostics_panel.setPlainText(f"provider=error | error={error_message}")
        self.retrieval_stage_panel.setPlainText("检索：失败\n粗排：失败\nBGE：失败\n上下文构造：失败")
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
        self._append_stream_chunk()

    def _append_stream_chunk(self) -> None:
        if not self._pending_stream_text:
            self._finish_streaming_response()
            return
        next_chunk = self._pending_stream_text[: self._stream_chunk_size]
        self._pending_stream_text = self._pending_stream_text[self._stream_chunk_size :]
        self._append_chat_text(next_chunk)
        if not self._pending_stream_text:
            self._finish_streaming_response()

    def _append_chat_text(self, text: str) -> None:
        cursor = self.chat_history.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        self.chat_history.setTextCursor(cursor)
        self.chat_history.insertPlainText(text)
        self._record_first_visible_token_if_needed()

    def _record_first_visible_token_if_needed(self) -> None:
        if self._first_visible_token_recorded or self._request_started_at <= 0:
            return
        self._first_visible_token_recorded = True
        first_token_latency_ms = max(0, int(round((time.monotonic() - self._request_started_at) * 1000)))
        if self._pending_first_token_latency_ms <= 0:
            self._pending_first_token_latency_ms = first_token_latency_ms
        self._update_provider_panels(total_in_progress=True)

    def _finish_streaming_response(self) -> None:
        self._stream_timer.stop()
        self._provider_stream_timer.stop()
        response = self._pending_stream_response
        answer_backend = self._pending_answer_backend
        provider_status = self._pending_provider_status
        provider_error = self._pending_provider_error
        provider_attempts = self._pending_provider_attempts
        first_token_latency_ms = self._pending_first_token_latency_ms
        total_latency_ms = self._pending_total_latency_ms
        provider_diagnostic = self._pending_provider_diagnostic
        retrieval_stage_latency_ms = dict(self._pending_retrieval_stage_latency_ms)
        retrieval_backend = getattr(self, "_pending_retrieval_backend", describe_retrieval_backend(self.settings))
        embedding_backend = getattr(self, "_pending_embedding_backend", describe_embedding_backend(self.settings))
        reranker_backend = getattr(self, "_pending_reranker_backend", describe_reranker_backend(self.settings))
        plan_route = getattr(self, "_pending_plan_route", "")
        plan_steps = getattr(self, "_pending_plan_steps", [])
        node_trace = getattr(self, "_pending_node_trace", [])
        tool_actions = getattr(self, "_pending_tool_actions", [])
        recovery_action = getattr(self, "_pending_recovery_action", "")
        replan_steps = getattr(self, "_pending_replan_steps", [])
        streamed_from_provider = self._streaming_from_provider
        self._pending_stream_response = None
        self._pending_stream_text = ""
        self._pending_provider_deltas = []
        self._pending_provider_completed_response = None
        self._streaming_from_provider = False
        self._pending_answer_backend = "unknown"
        self._pending_provider_status = "not_used"
        self._pending_provider_error = ""
        self._pending_provider_attempts = 0
        self._pending_first_token_latency_ms = 0
        self._pending_total_latency_ms = 0
        self._pending_provider_diagnostic = ""
        self._pending_retrieval_stage_latency_ms = {}
        self._pending_retrieval_backend = describe_retrieval_backend(self.settings)
        self._pending_embedding_backend = describe_embedding_backend(self.settings)
        self._pending_reranker_backend = describe_reranker_backend(self.settings)
        self._pending_plan_route = ""
        self._pending_plan_steps = []
        self._pending_node_trace = []
        self._pending_tool_actions = []
        self._pending_recovery_action = ""
        self._pending_replan_steps = []
        self._request_started_at = 0.0
        self._first_visible_token_recorded = False
        if self._ignore_current_response or response is None:
            self.request_status.setText("状态：已取消")
            self.provider_metrics_panel.setPlainText("首包延迟：已取消\n总耗时：已取消")
            self.provider_diagnostics_panel.setPlainText("provider=cancelled")
            self.retrieval_stage_panel.setPlainText("检索：已取消\n粗排：已取消\nBGE：已取消\n上下文构造：已取消")
            self._set_controls(send_enabled=True, cancel_enabled=False, retry_enabled=bool(self._last_query))
            return

        self.chat_history.append("")
        self._render_provider_panels(
            first_token_latency_ms=first_token_latency_ms,
            total_latency_ms=total_latency_ms,
            provider_diagnostic=provider_diagnostic,
        )
        self._render_retrieval_stage_panel(retrieval_stage_latency_ms)
        status_text = (
            f"状态：已完成 | 回答来源：{answer_backend} | "
            f"provider={provider_status} | attempts={provider_attempts} | "
            f"retrieval={retrieval_backend} | embedding={embedding_backend} | reranker={reranker_backend}"
        )
        if first_token_latency_ms > 0:
            status_text += f" | first_token={first_token_latency_ms}ms"
        if total_latency_ms > 0:
            status_text += f" | total={total_latency_ms}ms"
        if streamed_from_provider:
            status_text += " | stream=provider"
        if plan_route:
            status_text += f" | plan={plan_route}"
        if plan_steps:
            status_text += f" | steps={'>'.join(plan_steps)}"
        if node_trace:
            status_text += f" | trace={'>'.join(node_trace)}"
        if tool_actions:
            tool_names = ",".join(str(action.get("tool_name", "")) for action in tool_actions)
            status_text += f" | actions={len(tool_actions)} | tools={tool_names}"
        if recovery_action:
            status_text += f" | recovery={recovery_action}"
        if replan_steps:
            status_text += f" | replan={'>'.join(replan_steps)}"
        if provider_error:
            status_text += f" | error={provider_error}"
        self.request_status.setText(status_text)
        self._set_controls(send_enabled=True, cancel_enabled=False, retry_enabled=bool(self._last_query))

    def _handle_request_timeout(self) -> None:
        if self._request_thread is None:
            return
        self._ignore_current_response = True
        self.request_status.setText("状态：请求超时，可重试")
        elapsed_ms = max(0, int(round((time.monotonic() - self._request_started_at) * 1000))) if self._request_started_at else 0
        self.provider_metrics_panel.setPlainText(f"首包延迟：未返回\n总耗时：{elapsed_ms} ms")
        self.provider_diagnostics_panel.setPlainText("provider=timeout | client=timeout")
        self.retrieval_stage_panel.setPlainText("检索：超时\n粗排：超时\nBGE：超时\n上下文构造：超时")
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
        self.provider_metrics_panel.setPlainText("首包延迟：已取消\n总耗时：已取消")
        self.provider_diagnostics_panel.setPlainText("provider=cancelled")
        self.retrieval_stage_panel.setPlainText("检索：已取消\n粗排：已取消\nBGE：已取消\n上下文构造：已取消")
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
        summary = getattr(response, "summary", "")
        self.session_summary_panel.setPlainText(f"当前会话摘要：{summary or '暂无'}")
        retrieval_backend = getattr(response, "retrieval_backend", describe_retrieval_backend(self.settings))
        embedding_backend = getattr(response, "embedding_backend", describe_embedding_backend(self.settings))
        reranker_backend = getattr(response, "reranker_backend", describe_reranker_backend(self.settings))
        self.retrieval_status.setText(f"Retrieval 后端：{retrieval_backend}")
        self.embedding_status.setText(f"Embedding 后端：{embedding_backend}")
        self.reranker_status.setText(f"Reranker 后端：{reranker_backend}")

        self.sources_panel.clear()
        for source in response.sources:
            self.sources_panel.append(SourceCard(source).render_text())
            self.sources_panel.append("")

        self.tool_log_panel = ToolLogPanel()
        self.tool_logs_panel.clear()
        for log in response.tool_logs:
            self.tool_log_panel.add_log(log)
        self.tool_logs_panel.setPlainText(self.tool_log_panel.render_text())

    def _update_provider_panels(self, *, total_in_progress: bool) -> None:
        total_text = "进行中..." if total_in_progress else self._format_latency(self._pending_total_latency_ms)
        first_token_text = self._format_latency(self._pending_first_token_latency_ms)
        self.provider_metrics_panel.setPlainText(
            f"首包延迟：{first_token_text}\n总耗时：{total_text}"
        )
        diagnostic_text = self._pending_provider_diagnostic or f"provider={self._pending_provider_status}"
        self.provider_diagnostics_panel.setPlainText(diagnostic_text)

    def _render_provider_panels(
        self,
        *,
        first_token_latency_ms: int,
        total_latency_ms: int,
        provider_diagnostic: str,
    ) -> None:
        self.provider_metrics_panel.setPlainText(
            f"首包延迟：{self._format_latency(first_token_latency_ms)}\n"
            f"总耗时：{self._format_latency(total_latency_ms)}"
        )
        self.provider_diagnostics_panel.setPlainText(provider_diagnostic or "暂无 provider 诊断")

    def _render_retrieval_stage_panel(self, stage_latency_ms: dict[str, int]) -> None:
        self.retrieval_stage_panel.setPlainText(
            "\n".join(
                [
                    f"检索：{self._format_latency(stage_latency_ms.get('retrieval', 0))}",
                    f"粗排：{self._format_latency(stage_latency_ms.get('coarse_rerank', 0))}",
                    f"BGE：{self._format_latency(stage_latency_ms.get('bge_rerank', 0))}",
                    f"上下文构造：{self._format_latency(stage_latency_ms.get('context_build', 0))}",
                ]
            )
        )

    def _format_latency(self, latency_ms: int) -> str:
        if latency_ms <= 0:
            return "暂无"
        return f"{latency_ms} ms"
