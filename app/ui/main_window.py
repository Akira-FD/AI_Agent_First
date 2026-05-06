from __future__ import annotations

from dataclasses import dataclass
from html import escape
from pathlib import Path
import time
from types import SimpleNamespace

from app.ui.pages.chat_page import ChatPage
from app.ui.pages.docs_page import DocsPage
from app.ui.pages.logs_page import LogsPage
from app.ui.widgets.message_bubble import MessageBubble
from app.ui.widgets.source_card import SourceCard
from app.ui.widgets.tool_log_panel import ToolLogPanel

try:
    from PyQt6.QtCore import QObject, QThread, QTimer, Qt, pyqtSignal
    from PyQt6.QtGui import QTextCursor
    from PyQt6.QtWidgets import (
        QApplication,
        QFrame,
        QHBoxLayout,
        QLabel,
        QListWidget,
        QMainWindow,
        QPushButton,
        QScrollArea,
        QSplitter,
        QTextBrowser,
        QTextEdit,
        QVBoxLayout,
        QWidget,
    )
except ModuleNotFoundError:
    QApplication = None
    QFrame = None
    QLabel = None
    QObject = object
    QHBoxLayout = None
    QListWidget = None
    QMainWindow = object
    QThread = None
    QTimer = None
    QPushButton = None
    QScrollArea = None
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
    primary_screen = None
    primary_screen_getter = getattr(app, "primaryScreen", None)
    if callable(primary_screen_getter):
        primary_screen = primary_screen_getter()
    window.apply_startup_geometry(primary_screen)
    window.center_on_screen(primary_screen)
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
        self._conversation_messages: list[dict[str, object]] = []

        self.setWindowTitle(settings.app_name)
        self.setMinimumSize(1280, 820)
        self.resize(1480, 900)
        self._apply_theme()
        self._build_layout()
        self.refresh_documents()

    def _apply_theme(self) -> None:
        self.setStyleSheet(
            """
            QMainWindow {
                background: #f3efe6;
                color: #1f2933;
                font-family: "Segoe UI", "Microsoft YaHei";
            }
            QWidget {
                color: #1f2933;
                font-family: "Segoe UI", "Microsoft YaHei";
                background: transparent;
            }
            QWidget#AppRoot {
                background: qlineargradient(
                    x1: 0, y1: 0, x2: 1, y2: 1,
                    stop: 0 #f5f1e8,
                    stop: 0.55 #efe8db,
                    stop: 1 #e5dccd
                );
            }
            QFrame#HeroPanel {
                background: qlineargradient(
                    x1: 0, y1: 0, x2: 1, y2: 1,
                    stop: 0 #183a45,
                    stop: 0.45 #245c63,
                    stop: 1 #e48b51
                );
                border: 1px solid rgba(255, 255, 255, 0.18);
                border-radius: 26px;
            }
            QFrame#SurfaceCard {
                background: rgba(255, 251, 245, 0.96);
                border: 1px solid #d5c8b6;
                border-radius: 22px;
            }
            QFrame#ComposerCard {
                background: #f8f2e8;
                border: 1px solid #dcccb5;
                border-radius: 18px;
            }
            QLabel#HeroKicker {
                color: rgba(255, 248, 237, 0.9);
                font-size: 11px;
                font-weight: 700;
                letter-spacing: 1.5px;
            }
            QLabel#HeroTitle {
                color: #fffdfa;
                font-size: 30px;
                font-weight: 700;
            }
            QLabel#HeroSubtitle {
                color: rgba(255, 248, 237, 0.92);
                font-size: 13px;
                line-height: 1.4em;
            }
            QLabel {
                background: transparent;
            }
            QLabel#SectionTitle {
                color: #1d2a2e;
                font-size: 16px;
                font-weight: 700;
            }
            QLabel#SectionHint {
                color: #6b7280;
                font-size: 12px;
            }
            QLabel#RequestStatus {
                color: #17313a;
                font-size: 13px;
                font-weight: 600;
                padding: 12px 14px;
                background: #f6efe2;
                border: 1px solid #ddceb8;
                border-radius: 16px;
            }
            QListWidget#DocsList,
            QTextBrowser#SideBrowser,
            QTextBrowser#ChatHistory,
            QTextEdit#ComposerInput {
                background: rgba(255, 252, 248, 0.98);
                border: 1px solid #ddceb8;
                border-radius: 18px;
                padding: 8px 10px;
                selection-background-color: #c8dfe1;
            }
            QListWidget#DocsList {
                outline: 0;
            }
            QListWidget#DocsList::item {
                padding: 10px 8px;
                margin: 4px 2px;
                border-radius: 12px;
            }
            QListWidget#DocsList::item:selected {
                background: #d8e8e8;
                color: #163136;
            }
            QTextBrowser#ChatHistory {
                padding: 0;
            }
            QTextEdit#ComposerInput {
                font-size: 13px;
            }
            QPushButton {
                border-radius: 14px;
                padding: 11px 16px;
                font-weight: 600;
                border: 1px solid transparent;
            }
            QPushButton#PrimaryButton {
                background: #b95a37;
                color: #fffaf4;
                border-color: #a64c2b;
            }
            QPushButton#PrimaryButton:hover:!disabled {
                background: #a84e2e;
            }
            QPushButton#SecondaryButton {
                background: #e6ddd0;
                color: #24353a;
                border-color: #cfbfa8;
            }
            QPushButton#SecondaryButton:hover:!disabled {
                background: #ded1bf;
            }
            QPushButton#GhostButton {
                background: transparent;
                color: #38555c;
                border-color: #cdbca4;
            }
            QPushButton#GhostButton:hover:!disabled {
                background: rgba(33, 70, 77, 0.08);
            }
            QPushButton:disabled {
                background: #d4ccbf;
                color: #f8f4ed;
                border-color: #d4ccbf;
            }
            QSplitter::handle {
                background: transparent;
                width: 12px;
            }
            """
        )

    def _build_layout(self) -> None:
        root = QWidget()
        root.setObjectName("AppRoot")
        root_layout = QVBoxLayout(root)
        root_layout.setContentsMargins(18, 18, 18, 18)
        root_layout.setSpacing(14)

        hero = QFrame()
        hero.setObjectName("HeroPanel")
        hero_layout = QVBoxLayout(hero)
        hero_layout.setContentsMargins(28, 24, 28, 24)
        hero_layout.setSpacing(8)

        kicker = QLabel("AI_AGENT_FIRST / DESKTOP WORKBENCH")
        kicker.setObjectName("HeroKicker")
        hero_layout.addWidget(kicker)

        header = QLabel(f"{self.settings.app_name} 桌面端智能助理")
        header.setObjectName("HeroTitle")
        header.setWordWrap(True)
        hero_layout.addWidget(header)

        subheader = QLabel("面向真实问答链路的本地工作台，统一承载 RAG 检索、Agent 执行、SSE 流式回答、遥测诊断与会话摘要。")
        subheader.setObjectName("HeroSubtitle")
        subheader.setWordWrap(True)
        hero_layout.addWidget(subheader)

        backend = describe_llm_backend(self.settings, self.llm_service)
        self.backend_status = QLabel(f"LLM 后端：{backend}")
        self.retrieval_status = QLabel(f"Retrieval 后端：{describe_retrieval_backend(self.settings)}")
        self.embedding_status = QLabel(f"Embedding 后端：{describe_embedding_backend(self.settings)}")
        self.reranker_status = QLabel(f"Reranker 后端：{describe_reranker_backend(self.settings)}")

        badge_row = QWidget()
        badge_layout = QHBoxLayout(badge_row)
        badge_layout.setContentsMargins(0, 4, 0, 0)
        badge_layout.setSpacing(10)
        for label, tone in [
            (self.backend_status, "#d5efe9"),
            (self.retrieval_status, "#e8f0cf"),
            (self.embedding_status, "#f5e3ba"),
            (self.reranker_status, "#efd7dd"),
        ]:
            self._style_status_badge(label, tone)
            badge_layout.addWidget(label)
        badge_layout.addStretch(1)
        hero_layout.addWidget(badge_row)
        root_layout.addWidget(hero)

        status_card = self._create_surface_card()
        status_layout = QVBoxLayout(status_card)
        status_layout.setContentsMargins(18, 14, 18, 14)
        status_layout.setSpacing(6)
        status_header = QWidget()
        status_header_layout = QHBoxLayout(status_header)
        status_header_layout.setContentsMargins(0, 0, 0, 0)
        status_header_layout.setSpacing(10)
        status_title = QLabel("当前请求状态")
        status_title.setObjectName("SectionTitle")
        status_header_layout.addWidget(status_title)
        status_header_layout.addStretch(1)
        self.demo_state_button = QPushButton("载入演示态")
        self.demo_state_button.setObjectName("SecondaryButton")
        self.demo_state_button.clicked.connect(self.load_demo_state)
        status_header_layout.addWidget(self.demo_state_button)
        self.snapshot_button = QPushButton("导出快照")
        self.snapshot_button.setObjectName("GhostButton")
        self.snapshot_button.clicked.connect(self.export_current_snapshot)
        status_header_layout.addWidget(self.snapshot_button)
        status_layout.addWidget(status_header)
        self.request_status = QLabel("状态：空闲")
        self.request_status.setObjectName("RequestStatus")
        self.request_status.setWordWrap(True)
        status_layout.addWidget(self.request_status)
        root_layout.addWidget(status_card)

        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.setChildrenCollapsible(False)
        splitter.setHandleWidth(12)
        splitter.addWidget(self._build_docs_panel())
        splitter.addWidget(self._build_chat_panel())
        splitter.addWidget(self._build_side_panel())
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 8)
        splitter.setStretchFactor(2, 5)
        splitter.setSizes([205, 855, 420])
        self.workspace_splitter = splitter
        root_layout.addWidget(splitter)
        self.setCentralWidget(root)

    def showEvent(self, event) -> None:
        super().showEvent(event)
        if QTimer is not None:
            QTimer.singleShot(0, self._rebalance_workspace_splitter)

    def apply_startup_geometry(self, screen=None) -> None:
        screen = screen or self.screen()
        if screen is None and QApplication is not None:
            app = QApplication.instance()
            if app is not None:
                primary_screen_getter = getattr(app, "primaryScreen", None)
                if callable(primary_screen_getter):
                    screen = primary_screen_getter()
        if screen is None:
            return

        available = screen.availableGeometry()
        max_width = max(self.minimumWidth(), available.width() - 48)
        max_height = max(self.minimumHeight(), available.height() - 56)
        target_width = min(max_width, 1560)
        target_height = min(max_height, 940)

        if target_width < self.width():
            target_width = max(self.minimumWidth(), target_width)
        else:
            target_width = max(self.width(), target_width)

        if target_height < self.height():
            target_height = max(self.minimumHeight(), target_height)
        else:
            target_height = max(self.height(), target_height)

        self.resize(target_width, target_height)

    def center_on_screen(self, screen=None) -> None:
        screen = screen or self.screen()
        if screen is None and QApplication is not None:
            app = QApplication.instance()
            if app is not None:
                primary_screen_getter = getattr(app, "primaryScreen", None)
                if callable(primary_screen_getter):
                    screen = primary_screen_getter()
        if screen is None:
            return

        frame = self.frameGeometry()
        frame.moveCenter(screen.availableGeometry().center())
        self.move(frame.topLeft())

    def _build_docs_panel(self):
        panel = self._create_surface_card()
        panel.setMinimumWidth(200)
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(16, 14, 16, 14)
        layout.setSpacing(8)

        title = QLabel("知识库摘要")
        title.setObjectName("SectionTitle")
        layout.addWidget(title)
        hint = QLabel("聚焦覆盖领域、检索规模与核心主题。")
        hint.setObjectName("SectionHint")
        hint.setWordWrap(True)
        layout.addWidget(hint)

        meta_row = QWidget()
        meta_layout = QHBoxLayout(meta_row)
        meta_layout.setContentsMargins(0, 0, 0, 0)
        meta_layout.setSpacing(8)
        self.docs_count_badge = QLabel("0 文档")
        self._style_status_badge(self.docs_count_badge, "#d7e7e5")
        meta_layout.addWidget(self.docs_count_badge)
        self.docs_chunk_badge = QLabel("0 分块")
        self._style_status_badge(self.docs_chunk_badge, "#efe4c8")
        meta_layout.addWidget(self.docs_chunk_badge)
        meta_layout.addStretch(1)

        refresh_button = QPushButton("刷新文档")
        refresh_button.setObjectName("SecondaryButton")
        refresh_button.clicked.connect(self.refresh_documents)
        meta_layout.addWidget(refresh_button)
        layout.addWidget(meta_row)

        self.docs_summary_panel = QTextBrowser()
        self.docs_summary_panel.setObjectName("SideBrowser")
        self.docs_summary_panel.setMaximumHeight(260)
        self._set_browser_html(
            self.docs_summary_panel,
            "知识库摘要",
            "<div class='empty-state'>暂无知识库摘要</div>",
            subtitle="展示知识覆盖与关键主题。",
        )
        layout.addWidget(self.docs_summary_panel)
        layout.addStretch(1)
        return panel

    def _build_chat_panel(self):
        panel = self._create_surface_card()
        panel.setMinimumWidth(620)
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(18, 16, 18, 16)
        layout.setSpacing(10)

        title = QLabel("实时对话")
        title.setObjectName("SectionTitle")
        layout.addWidget(title)
        hint = QLabel("采用 SSE 流式输出，支持取消当前请求、超时提示与一键重试。")
        hint.setObjectName("SectionHint")
        hint.setWordWrap(True)
        layout.addWidget(hint)

        self.chat_history = QTextBrowser()
        self.chat_history.setObjectName("ChatHistory")
        layout.addWidget(self.chat_history)
        self._render_chat_history()

        composer = QFrame()
        composer.setObjectName("ComposerCard")
        composer_layout = QVBoxLayout(composer)
        composer_layout.setContentsMargins(12, 12, 12, 12)
        composer_layout.setSpacing(10)

        composer_title = QLabel("提问输入区")
        composer_title.setObjectName("SectionTitle")
        composer_layout.addWidget(composer_title)

        input_layout = QHBoxLayout()
        input_layout.setContentsMargins(0, 0, 0, 0)
        input_layout.setSpacing(12)
        self.input_box = QTextEdit()
        self.input_box.setObjectName("ComposerInput")
        self.input_box.setPlaceholderText("输入问题，例如：请先查询 redis 状态，再查一下 timeout 日志，最后给我总结根因")
        self.input_box.setFixedHeight(110)
        self.send_button = QPushButton("发送请求")
        self.send_button.setObjectName("PrimaryButton")
        self.send_button.clicked.connect(self.handle_send)
        self.cancel_button = QPushButton("取消")
        self.cancel_button.setObjectName("SecondaryButton")
        self.cancel_button.setEnabled(False)
        self.cancel_button.clicked.connect(self.cancel_current_request)
        self.retry_button = QPushButton("重试")
        self.retry_button.setObjectName("GhostButton")
        self.retry_button.setEnabled(False)
        self.retry_button.clicked.connect(self.retry_last_query)
        input_layout.addWidget(self.input_box)
        action_column = QVBoxLayout()
        action_column.setContentsMargins(0, 0, 0, 0)
        action_column.setSpacing(10)
        action_column.addWidget(self.send_button)
        action_column.addWidget(self.cancel_button)
        action_column.addWidget(self.retry_button)
        action_column.addStretch(1)
        input_layout.addLayout(action_column)
        composer_layout.addLayout(input_layout)
        layout.addWidget(composer)
        return panel

    def _build_side_panel(self):
        panel = self._create_surface_card()
        panel.setMinimumWidth(320)
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(18, 16, 18, 16)
        layout.setSpacing(10)

        title = QLabel("可观测性与上下文")
        title.setObjectName("SectionTitle")
        layout.addWidget(title)
        hint = QLabel("右侧聚合展示耗时、Provider 诊断、RAG 阶段信息、会话摘要、来源引用和工具日志。")
        hint.setObjectName("SectionHint")
        hint.setWordWrap(True)
        layout.addWidget(hint)

        self.side_scroll_area = QScrollArea()
        self.side_scroll_area.setWidgetResizable(True)
        self.side_scroll_area.setFrameShape(QFrame.Shape.NoFrame)
        self.side_scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.side_scroll_area.setStyleSheet(
            "QScrollArea { background: transparent; border: none; }"
            "QScrollBar:vertical { width: 10px; background: transparent; margin: 4px 0; }"
            "QScrollBar::handle:vertical { background: #ccb99d; border-radius: 5px; min-height: 24px; }"
            "QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }"
        )
        side_content = QWidget()
        side_content_layout = QVBoxLayout(side_content)
        side_content_layout.setContentsMargins(0, 0, 0, 0)
        side_content_layout.setSpacing(10)

        self.provider_metrics_panel = QTextBrowser()
        self.provider_metrics_panel.setObjectName("SideBrowser")
        self.provider_metrics_panel.setMaximumHeight(120)
        self._set_browser_html(
            self.provider_metrics_panel,
            "请求指标",
            "<div class='metric-grid'><div class='metric-item'><span class='metric-label'>首包延迟：</span><span class='metric-value'>暂无</span></div>"
            "<div class='metric-item'><span class='metric-label'>总耗时：</span><span class='metric-value'>暂无</span></div></div>",
        )
        side_content_layout.addWidget(self.provider_metrics_panel)
        self.provider_diagnostics_panel = QTextBrowser()
        self.provider_diagnostics_panel.setObjectName("SideBrowser")
        self.provider_diagnostics_panel.setMaximumHeight(130)
        self._set_browser_html(
            self.provider_diagnostics_panel,
            "Provider 诊断",
            "<div class='diagnostic-copy'>暂无 provider 诊断</div>",
        )
        side_content_layout.addWidget(self.provider_diagnostics_panel)
        self.retrieval_stage_panel = QTextBrowser()
        self.retrieval_stage_panel.setObjectName("SideBrowser")
        self.retrieval_stage_panel.setMaximumHeight(155)
        self._set_browser_html(
            self.retrieval_stage_panel,
            "RAG 阶段耗时",
            self._build_stage_metric_html({}),
        )
        side_content_layout.addWidget(self.retrieval_stage_panel)
        self.session_summary_panel = QTextBrowser()
        self.session_summary_panel.setObjectName("SideBrowser")
        self.session_summary_panel.setMaximumHeight(180)
        self._set_browser_html(
            self.session_summary_panel,
            "当前会话摘要",
            "<div class='summary-copy'>当前会话摘要：暂无</div>",
        )
        side_content_layout.addWidget(self.session_summary_panel)
        self.sources_panel = QTextBrowser()
        self.sources_panel.setObjectName("SideBrowser")
        self._set_browser_html(
            self.sources_panel,
            "来源引用",
            "<div class='empty-state'>暂无引用来源</div>",
        )
        side_content_layout.addWidget(self.sources_panel)
        self.tool_logs_panel = QTextBrowser()
        self.tool_logs_panel.setObjectName("SideBrowser")
        self._set_browser_html(
            self.tool_logs_panel,
            "工具日志",
            "<div class='tool-log-empty'>暂无工具调用</div>",
        )
        side_content_layout.addWidget(self.tool_logs_panel)
        side_content_layout.addStretch(1)
        self.side_scroll_area.setWidget(side_content)
        layout.addWidget(self.side_scroll_area)
        return panel

    def _rebalance_workspace_splitter(self) -> None:
        splitter = getattr(self, "workspace_splitter", None)
        if splitter is None:
            return
        available_width = splitter.width() - (splitter.handleWidth() * 2)
        if available_width <= 0:
            return

        docs_width = max(200, int(available_width * 0.135))
        side_width = max(320, int(available_width * 0.285))
        chat_width = max(640, available_width - docs_width - side_width)

        total = docs_width + chat_width + side_width
        if total > available_width:
            overflow = total - available_width
            reducible_chat = max(0, chat_width - 640)
            take = min(reducible_chat, overflow)
            chat_width -= take
            overflow -= take

            reducible_docs = max(0, docs_width - 200)
            take = min(reducible_docs, overflow)
            docs_width -= take
            overflow -= take

            reducible_side = max(0, side_width - 320)
            take = min(reducible_side, overflow)
            side_width -= take

        splitter.setSizes([docs_width, chat_width, side_width])

    def load_demo_state(self) -> None:
        self._conversation_messages = [
            {
                "role": "user",
                "content": "请先检查 Redis 状态，再看 timeout 日志，最后总结当前最可能的根因。",
            },
            {
                "role": "assistant",
                "content": (
                    "已先完成基础诊断：Redis 服务状态正常，但最近 15 分钟内出现了多次 timeout。"
                    "建议优先检查连接数峰值、慢查询日志，以及上游请求是否在流量高峰期出现重试放大。"
                ),
            },
        ]
        self._render_chat_history()

        demo_response = SimpleNamespace(
            answer=self._conversation_messages[-1]["content"],
            summary="本轮会话围绕 Redis timeout 排查，已结合工具日志与知识库给出优先排查顺序。",
            sources=[
                {
                    "title": "Redis 故障排查",
                    "source": "redis-troubleshooting.md",
                    "section_path": "Redis > 故障排查 > timeout",
                    "score": 4.8,
                    "excerpt": "timeout 高频出现时，先看连接池耗尽、慢查询堆积和网络重传。",
                },
                {
                    "title": "Kubernetes 服务稳定性",
                    "source": "kubernetes-ops.md",
                    "section_path": "Kubernetes > Service > 超时排查",
                    "score": 4.3,
                    "excerpt": "若 Redis 运行在集群内，还需关注节点负载与跨可用区延迟。",
                },
            ],
            tool_logs=[
                {
                    "tool_name": "check_service_status",
                    "status": "success",
                    "message": "Redis service is running, uptime 4d 12h.",
                },
                {
                    "tool_name": "search_error_logs",
                    "status": "success",
                    "message": "Matched 12 timeout entries in the last 15 minutes.",
                },
                {
                    "tool_name": "restart_mock_service",
                    "status": "skipped",
                    "message": "No restart performed because service health remained stable.",
                },
            ],
            retrieval_backend=describe_retrieval_backend(self.settings),
            embedding_backend=describe_embedding_backend(self.settings),
            reranker_backend=describe_reranker_backend(self.settings),
        )
        self._render_response_metadata(demo_response)
        self._render_provider_panels(
            first_token_latency_ms=620,
            total_latency_ms=2140,
            provider_diagnostic=(
                "provider=http_429 | attempts=2 | retry_backoff=0.4s | "
                "fallback=remote_retry_recovered"
            ),
        )
        self._render_retrieval_stage_panel(
            {
                "retrieval": 84,
                "coarse_rerank": 19,
                "bge_rerank": 57,
                "context_build": 13,
            }
        )
        self.request_status.setText(
            "状态：已完成 | 回答来源：remote | provider=http_429_then_success | attempts=2 "
            "| retrieval=milvus-lite | embedding=hash | reranker=bge | first_token=620ms | total=2140ms"
        )

    def export_snapshot(self, path: str | Path) -> bool:
        output = Path(path)
        output.parent.mkdir(parents=True, exist_ok=True)
        app = QApplication.instance() if QApplication is not None else None
        if app is not None:
            app.processEvents()
        pixmap = self.grab()
        if pixmap.isNull():
            return False
        return pixmap.save(str(output))

    def export_current_snapshot(self, path: str | Path | None = None) -> Path | None:
        output = Path(path) if path is not None else Path.cwd() / "results" / "latest_desktop_snapshot.png"
        if not self.export_snapshot(output):
            self.request_status.setText("状态：导出快照失败")
            return None
        self.request_status.setText(f"状态：已导出快照 | {output}")
        return output

    def _create_surface_card(self) -> QFrame:
        panel = QFrame()
        panel.setObjectName("SurfaceCard")
        return panel

    def _style_status_badge(self, label: QLabel, background: str) -> None:
        label.setStyleSheet(
            f"padding: 6px 10px; border-radius: 999px; background: {background}; "
            "color: #17313a; font-size: 12px; font-weight: 600;"
        )

    def _set_browser_html(self, browser: QTextBrowser, title: str, body_html: str, subtitle: str = "") -> None:
        browser.setHtml(
            f"""
            <html>
              <head>
                <style>
                  body {{
                    font-family: "Segoe UI", "Microsoft YaHei";
                    margin: 0;
                    color: #24353a;
                    background: transparent;
                  }}
                  .panel-shell {{
                    padding: 2px;
                  }}
                  .panel-title {{
                    font-size: 12px;
                    font-weight: 700;
                    color: #1f2b2e;
                    margin-bottom: 6px;
                    letter-spacing: 0.4px;
                  }}
                  .panel-subtitle {{
                    font-size: 11px;
                    color: #7b7f82;
                    margin-bottom: 10px;
                  }}
                  .metric-grid {{
                    display: block;
                  }}
                  .compact-stat-grid {{
                    display: block;
                    margin-bottom: 8px;
                  }}
                  .compact-stat {{
                    border: 1px solid #e2d6c7;
                    border-radius: 14px;
                    background: #fcf8f1;
                    padding: 10px 12px;
                    margin-bottom: 7px;
                  }}
                  .compact-stat-label {{
                    display: block;
                    font-size: 11px;
                    color: #8b725f;
                    margin-bottom: 4px;
                  }}
                  .compact-stat-value {{
                    display: block;
                    font-size: 17px;
                    font-weight: 700;
                    color: #17313a;
                  }}
                  .metric-item {{
                    border: 1px solid #e2d6c7;
                    border-radius: 14px;
                    background: #fcf8f1;
                    padding: 10px 12px;
                    margin-bottom: 8px;
                  }}
                  .metric-label {{
                    font-size: 11px;
                    color: #8b725f;
                    margin-right: 6px;
                  }}
                  .metric-value {{
                    font-size: 15px;
                    font-weight: 700;
                    color: #17313a;
                  }}
                  .diagnostic-copy,
                  .summary-copy,
                  .empty-state,
                  .tool-log-empty {{
                    border: 1px solid #e2d6c7;
                    border-radius: 14px;
                    background: #fcf8f1;
                    padding: 12px;
                    color: #30444b;
                    line-height: 1.5em;
                  }}
                  .source-card,
                  .tool-log-card {{
                    border: 1px solid #e2d6c7;
                    border-radius: 16px;
                    background: #fcf8f1;
                    padding: 12px;
                    margin-bottom: 10px;
                  }}
                  .source-card-header,
                  .tool-log-header {{
                    display: block;
                    margin-bottom: 8px;
                  }}
                  .source-card-title,
                  .tool-name {{
                    font-size: 13px;
                    font-weight: 700;
                    color: #19343b;
                    margin-bottom: 6px;
                  }}
                  .source-card-meta,
                  .tool-log-message {{
                    font-size: 12px;
                    color: #56656a;
                    line-height: 1.5em;
                  }}
                  .score-pill,
                  .status-pill {{
                    display: inline-block;
                    padding: 4px 9px;
                    border-radius: 999px;
                    background: #d9ebe6;
                    color: #1a4247;
                    font-size: 11px;
                    font-weight: 700;
                    margin-bottom: 8px;
                  }}
                  .summary-section {{
                    border: 1px solid #e2d6c7;
                    border-radius: 14px;
                    background: #fcf8f1;
                    padding: 10px 12px;
                    margin-top: 8px;
                  }}
                  .summary-section-title {{
                    font-size: 11px;
                    font-weight: 700;
                    color: #8b725f;
                    margin-bottom: 6px;
                    letter-spacing: 0.2px;
                  }}
                  .topic-cloud {{
                    display: block;
                  }}
                  .topic-chip {{
                    display: inline-block;
                    padding: 5px 9px;
                    border-radius: 999px;
                    background: #efe4c8;
                    color: #5e4d39;
                    font-size: 11px;
                    font-weight: 700;
                    margin: 0 6px 6px 0;
                  }}
                  .stage-grid {{
                    display: block;
                  }}
                  .stage-item {{
                    border: 1px solid #e2d6c7;
                    border-radius: 14px;
                    background: #fcf8f1;
                    padding: 10px 12px;
                    margin-bottom: 8px;
                  }}
                  .stage-name {{
                    font-size: 11px;
                    color: #8b725f;
                    margin-right: 6px;
                  }}
                  .stage-value {{
                    font-size: 14px;
                    font-weight: 700;
                    color: #17313a;
                  }}
                </style>
              </head>
              <body>
                <div class="panel-shell">
                  <div class="panel-title">{escape(title)}</div>
                  {f'<div class="panel-subtitle">{escape(subtitle)}</div>' if subtitle else ''}
                  {body_html}
                </div>
              </body>
            </html>
            """
        )

    def _build_stage_metric_html(self, stage_latency_ms: dict[str, int]) -> str:
        items = [
            ("检索", stage_latency_ms.get("retrieval", 0)),
            ("粗排", stage_latency_ms.get("coarse_rerank", 0)),
            ("BGE", stage_latency_ms.get("bge_rerank", 0)),
            ("上下文构造", stage_latency_ms.get("context_build", 0)),
        ]
        return (
            "<div class='stage-grid'>"
            + "".join(
                f"<div class='stage-item'><span class='stage-name'>{escape(name)}：</span>"
                f"<span class='stage-value'>{escape(self._format_latency(value))}</span></div>"
                for name, value in items
            )
            + "</div>"
        )

    def _render_chat_history(self) -> None:
        if not self._conversation_messages:
            body_html = (
                "<div class='chat-empty'>"
                "<div class='chat-empty-title'>准备开始一次真实问答</div>"
                "<div class='chat-empty-copy'>"
                "左侧关注知识库覆盖，右侧实时观察 Provider 诊断、RAG 阶段耗时和工具执行信息。"
                "</div>"
                "</div>"
            )
        else:
            body_html = "<div class='chat-feed'>" + "".join(
                MessageBubble(str(message.get("role", "assistant")), str(message.get("content", ""))).render_html()
                for message in self._conversation_messages
            ) + "</div>"

        self.chat_history.setHtml(
            f"""
            <html>
              <head>
                <style>
                  body {{
                    font-family: "Segoe UI", "Microsoft YaHei";
                    margin: 0;
                    background: #fffaf4;
                    color: #22343a;
                  }}
                  .chat-shell {{
                    padding: 18px 18px 12px 18px;
                    background:
                      radial-gradient(circle at top right, rgba(219, 191, 146, 0.18), transparent 32%),
                      linear-gradient(180deg, #fffaf4 0%, #f8f1e6 100%);
                    min-height: 100%;
                  }}
                  .chat-empty {{
                    border: 1px dashed #d5c7b2;
                    border-radius: 20px;
                    background: rgba(255, 253, 248, 0.92);
                    padding: 20px 18px;
                    color: #47565c;
                  }}
                  .chat-empty-title {{
                    font-size: 15px;
                    font-weight: 700;
                    color: #19343b;
                    margin-bottom: 8px;
                  }}
                  .chat-empty-copy {{
                    font-size: 12px;
                    line-height: 1.6em;
                  }}
                  .message-row {{
                    width: 100%;
                    margin-bottom: 12px;
                  }}
                  .assistant-row {{
                    text-align: left;
                  }}
                  .user-row {{
                    text-align: right;
                  }}
                  .message-bubble {{
                    display: inline-block;
                    max-width: 84%;
                    border-radius: 20px;
                    padding: 12px 14px;
                    border: 1px solid #d7cab7;
                    box-shadow: 0 8px 20px rgba(41, 57, 62, 0.06);
                  }}
                  .assistant-bubble {{
                    background: #fffdf8;
                  }}
                  .user-bubble {{
                    background: #dbeae7;
                    border-color: #bdd7d2;
                  }}
                  .system-bubble {{
                    background: #f8efe0;
                    border-color: #e0ccaa;
                  }}
                  .message-role {{
                    font-size: 11px;
                    font-weight: 700;
                    color: #8a6f58;
                    margin-bottom: 6px;
                    letter-spacing: 0.4px;
                  }}
                  .message-content {{
                    font-size: 13px;
                    line-height: 1.6em;
                    color: #21363c;
                  }}
                  .message-placeholder {{
                    color: #9da6aa;
                  }}
                </style>
              </head>
              <body>
                <div class="chat-shell">{body_html}</div>
              </body>
            </html>
            """
        )
        cursor = self.chat_history.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        self.chat_history.setTextCursor(cursor)
        self.chat_history.ensureCursorVisible()

    def _add_conversation_message(self, role: str, content: str, *, streaming: bool = False) -> None:
        self._conversation_messages.append({"role": role, "content": content, "streaming": streaming})
        self._render_chat_history()

    def _ensure_streaming_assistant_message(self) -> None:
        if self._conversation_messages:
            last_message = self._conversation_messages[-1]
            if last_message.get("role") == "assistant" and last_message.get("streaming"):
                return
        self._add_conversation_message("assistant", "", streaming=True)

    def _append_to_streaming_assistant_message(self, text: str) -> None:
        self._ensure_streaming_assistant_message()
        self._conversation_messages[-1]["content"] = str(self._conversation_messages[-1].get("content", "")) + text
        self._render_chat_history()

    def _finalize_streaming_assistant_message(self, final_text: str | None = None, *, drop_if_empty: bool = False) -> None:
        if not self._conversation_messages:
            return
        last_message = self._conversation_messages[-1]
        if last_message.get("role") != "assistant" or not last_message.get("streaming"):
            return
        if final_text is not None:
            last_message["content"] = final_text
        if drop_if_empty and not str(last_message.get("content", "")).strip():
            self._conversation_messages.pop()
        else:
            last_message["streaming"] = False
        self._render_chat_history()

    def refresh_documents(self) -> None:
        documents = self.docs_page.refresh()
        self.docs_count_badge.setText(f"{len(documents)} 文档")
        summary = self.docs_page.build_summary()
        self.docs_chunk_badge.setText(f"{summary['chunk_count']} 分块")
        self._set_browser_html(
            self.docs_summary_panel,
            "知识库摘要",
            self._build_docs_summary_html(summary),
            subtitle="展示知识覆盖与关键主题。",
        )

    def _build_docs_summary_html(self, summary: dict[str, object]) -> str:
        category_labels = list(summary.get("category_labels", []))
        key_topics = list(summary.get("key_topics", []))
        if not category_labels and not key_topics:
            return "<div class='empty-state'>暂无知识库摘要</div>"

        category_html = "".join(
            f"<span class='score-pill'>{escape(str(label))}</span>"
            for label in category_labels[:3]
        )
        topic_html = "".join(
            f"<span class='topic-chip'>{escape(str(topic))}</span>"
            for topic in key_topics[:4]
        )
        document_count = escape(str(summary.get("document_count", 0)))
        chunk_count = escape(str(summary.get("chunk_count", 0)))
        fallback_category_html = '<span class="topic-chip">通用</span>'
        fallback_topic_html = '<span class="topic-chip">暂无</span>'
        return (
            "<div class='compact-stat-grid'>"
            "<div class='compact-stat'>"
            "<span class='compact-stat-label'>知识规模</span>"
            f"<span class='compact-stat-value'>{document_count} 份文档</span>"
            "</div>"
            "<div class='compact-stat'>"
            "<span class='compact-stat-label'>检索规模</span>"
            f"<span class='compact-stat-value'>{chunk_count} 个分块</span>"
            "</div>"
            "</div>"
            "<div class='summary-section'>"
            "<div class='summary-section-title'>覆盖领域</div>"
            f"{category_html or fallback_category_html}"
            "</div>"
            "<div class='summary-section'>"
            "<div class='summary-section-title'>核心主题</div>"
            f"<div class='topic-cloud'>{topic_html or fallback_topic_html}</div>"
            "</div>"
        )

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
        self._add_conversation_message("user", query)
        self._set_controls(send_enabled=False, cancel_enabled=True, retry_enabled=False)
        self.request_status.setText("状态：处理中...")
        self._set_browser_html(
            self.provider_metrics_panel,
            "请求指标",
            "<div class='metric-grid'><div class='metric-item'><span class='metric-label'>首包延迟：</span><span class='metric-value'>测量中...</span></div>"
            "<div class='metric-item'><span class='metric-label'>总耗时：</span><span class='metric-value'>进行中...</span></div></div>",
        )
        self._set_browser_html(
            self.provider_diagnostics_panel,
            "Provider 诊断",
            "<div class='diagnostic-copy'>provider=processing</div>",
        )
        self._set_browser_html(
            self.retrieval_stage_panel,
            "RAG 阶段耗时",
            self._build_stage_metric_html({"retrieval": -1, "coarse_rerank": 0, "bge_rerank": 0, "context_build": 0}),
        )
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
        self._ensure_streaming_assistant_message()
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
            self._ensure_streaming_assistant_message()
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
        self._finalize_streaming_assistant_message(drop_if_empty=True)
        self._add_conversation_message("assistant", f"请求失败，{error_message}")
        self.request_status.setText("状态：请求失败，可重试")
        self._set_browser_html(
            self.provider_metrics_panel,
            "请求指标",
            "<div class='metric-grid'><div class='metric-item'><span class='metric-label'>首包延迟：</span><span class='metric-value'>失败</span></div>"
            "<div class='metric-item'><span class='metric-label'>总耗时：</span><span class='metric-value'>失败</span></div></div>",
        )
        self._set_browser_html(
            self.provider_diagnostics_panel,
            "Provider 诊断",
            f"<div class='diagnostic-copy'>provider=error | error={escape(error_message)}</div>",
        )
        self._set_browser_html(
            self.retrieval_stage_panel,
            "RAG 阶段耗时",
            "<div class='stage-grid'>"
            "<div class='stage-item'><span class='stage-name'>检索</span><span class='stage-value'>失败</span></div>"
            "<div class='stage-item'><span class='stage-name'>粗排</span><span class='stage-value'>失败</span></div>"
            "<div class='stage-item'><span class='stage-name'>BGE</span><span class='stage-value'>失败</span></div>"
            "<div class='stage-item'><span class='stage-name'>上下文构造</span><span class='stage-value'>失败</span></div>"
            "</div>",
        )
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
        self._append_to_streaming_assistant_message(text)
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
            self._finalize_streaming_assistant_message(drop_if_empty=True)
            self.request_status.setText("状态：已取消")
            self._set_browser_html(
                self.provider_metrics_panel,
                "请求指标",
                "<div class='metric-grid'><div class='metric-item'><span class='metric-label'>首包延迟：</span><span class='metric-value'>已取消</span></div>"
                "<div class='metric-item'><span class='metric-label'>总耗时：</span><span class='metric-value'>已取消</span></div></div>",
            )
            self._set_browser_html(
                self.provider_diagnostics_panel,
                "Provider 诊断",
                "<div class='diagnostic-copy'>provider=cancelled</div>",
            )
            self._set_browser_html(
                self.retrieval_stage_panel,
                "RAG 阶段耗时",
                "<div class='stage-grid'>"
                "<div class='stage-item'><span class='stage-name'>检索</span><span class='stage-value'>已取消</span></div>"
                "<div class='stage-item'><span class='stage-name'>粗排</span><span class='stage-value'>已取消</span></div>"
                "<div class='stage-item'><span class='stage-name'>BGE</span><span class='stage-value'>已取消</span></div>"
                "<div class='stage-item'><span class='stage-name'>上下文构造</span><span class='stage-value'>已取消</span></div>"
                "</div>",
            )
            self._set_controls(send_enabled=True, cancel_enabled=False, retry_enabled=bool(self._last_query))
            return

        self._finalize_streaming_assistant_message(response.answer or None)
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
        self._set_browser_html(
            self.provider_metrics_panel,
            "请求指标",
            "<div class='metric-grid'>"
            "<div class='metric-item'><span class='metric-label'>首包延迟：</span><span class='metric-value'>未返回</span></div>"
            f"<div class='metric-item'><span class='metric-label'>总耗时：</span><span class='metric-value'>{escape(self._format_latency(elapsed_ms))}</span></div>"
            "</div>",
        )
        self._set_browser_html(
            self.provider_diagnostics_panel,
            "Provider 诊断",
            "<div class='diagnostic-copy'>provider=timeout | client=timeout</div>",
        )
        self._set_browser_html(
            self.retrieval_stage_panel,
            "RAG 阶段耗时",
            "<div class='stage-grid'>"
            "<div class='stage-item'><span class='stage-name'>检索</span><span class='stage-value'>超时</span></div>"
            "<div class='stage-item'><span class='stage-name'>粗排</span><span class='stage-value'>超时</span></div>"
            "<div class='stage-item'><span class='stage-name'>BGE</span><span class='stage-value'>超时</span></div>"
            "<div class='stage-item'><span class='stage-name'>上下文构造</span><span class='stage-value'>超时</span></div>"
            "</div>",
        )
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
        self._set_browser_html(
            self.provider_metrics_panel,
            "请求指标",
            "<div class='metric-grid'><div class='metric-item'><span class='metric-label'>首包延迟：</span><span class='metric-value'>已取消</span></div>"
            "<div class='metric-item'><span class='metric-label'>总耗时：</span><span class='metric-value'>已取消</span></div></div>",
        )
        self._set_browser_html(
            self.provider_diagnostics_panel,
            "Provider 诊断",
            "<div class='diagnostic-copy'>provider=cancelled</div>",
        )
        self._set_browser_html(
            self.retrieval_stage_panel,
            "RAG 阶段耗时",
            "<div class='stage-grid'>"
            "<div class='stage-item'><span class='stage-name'>检索</span><span class='stage-value'>已取消</span></div>"
            "<div class='stage-item'><span class='stage-name'>粗排</span><span class='stage-value'>已取消</span></div>"
            "<div class='stage-item'><span class='stage-name'>BGE</span><span class='stage-value'>已取消</span></div>"
            "<div class='stage-item'><span class='stage-name'>上下文构造</span><span class='stage-value'>已取消</span></div>"
            "</div>",
        )
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
        self._set_browser_html(
            self.session_summary_panel,
            "当前会话摘要",
            f"<div class='summary-copy'>当前会话摘要：{escape(summary or '暂无')}</div>",
        )
        retrieval_backend = getattr(response, "retrieval_backend", describe_retrieval_backend(self.settings))
        embedding_backend = getattr(response, "embedding_backend", describe_embedding_backend(self.settings))
        reranker_backend = getattr(response, "reranker_backend", describe_reranker_backend(self.settings))
        self.retrieval_status.setText(f"Retrieval 后端：{retrieval_backend}")
        self.embedding_status.setText(f"Embedding 后端：{embedding_backend}")
        self.reranker_status.setText(f"Reranker 后端：{reranker_backend}")

        for label, tone in [
            (self.retrieval_status, "#e8f0cf"),
            (self.embedding_status, "#f5e3ba"),
            (self.reranker_status, "#efd7dd"),
        ]:
            self._style_status_badge(label, tone)

        source_cards = "".join(SourceCard(source).render_html() for source in response.sources)
        self._set_browser_html(
            self.sources_panel,
            "来源引用",
            source_cards or "<div class='empty-state'>暂无引用来源</div>",
        )

        self.tool_log_panel = ToolLogPanel()
        for log in response.tool_logs:
            self.tool_log_panel.add_log(log)
        self._set_browser_html(
            self.tool_logs_panel,
            "工具日志",
            self.tool_log_panel.render_html(),
        )

    def _update_provider_panels(self, *, total_in_progress: bool) -> None:
        total_text = "进行中..." if total_in_progress else self._format_latency(self._pending_total_latency_ms)
        first_token_text = self._format_latency(self._pending_first_token_latency_ms)
        self._set_browser_html(
            self.provider_metrics_panel,
            "请求指标",
            "<div class='metric-grid'>"
            f"<div class='metric-item'><span class='metric-label'>首包延迟：</span><span class='metric-value'>{escape(first_token_text)}</span></div>"
            f"<div class='metric-item'><span class='metric-label'>总耗时：</span><span class='metric-value'>{escape(total_text)}</span></div>"
            "</div>",
        )
        diagnostic_text = self._pending_provider_diagnostic or f"provider={self._pending_provider_status}"
        self._set_browser_html(
            self.provider_diagnostics_panel,
            "Provider 诊断",
            f"<div class='diagnostic-copy'>{escape(diagnostic_text)}</div>",
        )

    def _render_provider_panels(
        self,
        *,
        first_token_latency_ms: int,
        total_latency_ms: int,
        provider_diagnostic: str,
    ) -> None:
        self._set_browser_html(
            self.provider_metrics_panel,
            "请求指标",
            "<div class='metric-grid'>"
            f"<div class='metric-item'><span class='metric-label'>首包延迟：</span><span class='metric-value'>{escape(self._format_latency(first_token_latency_ms))}</span></div>"
            f"<div class='metric-item'><span class='metric-label'>总耗时：</span><span class='metric-value'>{escape(self._format_latency(total_latency_ms))}</span></div>"
            "</div>",
        )
        self._set_browser_html(
            self.provider_diagnostics_panel,
            "Provider 诊断",
            f"<div class='diagnostic-copy'>{escape(provider_diagnostic or '暂无 provider 诊断')}</div>",
        )

    def _render_retrieval_stage_panel(self, stage_latency_ms: dict[str, int]) -> None:
        self._set_browser_html(
            self.retrieval_stage_panel,
            "RAG 阶段耗时",
            self._build_stage_metric_html(stage_latency_ms),
        )

    def _format_latency(self, latency_ms: int) -> str:
        if latency_ms <= 0:
            return "暂无"
        return f"{latency_ms} ms"
