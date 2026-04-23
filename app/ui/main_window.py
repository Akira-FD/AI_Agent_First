from __future__ import annotations

from dataclasses import dataclass

from app.ui.pages.chat_page import ChatPage
from app.ui.pages.docs_page import DocsPage
from app.ui.pages.logs_page import LogsPage
from app.ui.widgets.source_card import SourceCard
from app.ui.widgets.tool_log_panel import ToolLogPanel

try:
    from PyQt6.QtCore import Qt
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
    QHBoxLayout = None
    QListWidget = None
    QMainWindow = object
    QPushButton = None
    QSplitter = None
    QTextBrowser = None
    QTextEdit = None
    QVBoxLayout = None
    QWidget = None
    Qt = None


@dataclass
class DesktopAppShell:
    agent: object
    settings: object
    document_service: object | None = None

    def render_status(self) -> str:
        return (
            f"{self.settings.app_name} MVP shell is ready.\n"
            f"Docs directory: {self.settings.docs_dir}\n"
            "UI scaffold: sessions | chat | sources | tool logs"
        )

    def create_pages(self) -> dict[str, object]:
        return {
            "chat": ChatPage(agent=self.agent),
            "docs": DocsPage(document_service=self.document_service),
            "logs": LogsPage(),
        }


def launch_pyqt_app(agent, settings, document_service=None) -> int:
    if QApplication is None:
        raise RuntimeError("PyQt6 is not installed. Run `pip install PyQt6` before launching the desktop UI.")

    app = QApplication.instance() or QApplication([])
    window = MainWindow(agent=agent, settings=settings, document_service=document_service)
    window.resize(980, 680)
    window.show()
    return app.exec()


class MainWindow(QMainWindow):
    def __init__(self, agent, settings, document_service=None) -> None:
        super().__init__()
        if QApplication is None:
            raise RuntimeError("PyQt6 is not installed. Run `pip install PyQt6` before launching the desktop UI.")
        self.agent = agent
        self.settings = settings
        self.document_service = document_service
        self.chat_page = ChatPage(agent=agent, session_id="desktop")
        self.docs_page = DocsPage(document_service=document_service)
        self.tool_log_panel = ToolLogPanel()

        self.setWindowTitle(settings.app_name)
        self._build_layout()
        self.refresh_documents()

    def _build_layout(self) -> None:
        root = QWidget()
        root_layout = QVBoxLayout(root)
        header = QLabel(f"{self.settings.app_name} | 本地 MVP 演示")
        header.setStyleSheet("font-size: 18px; font-weight: 700; padding: 8px;")
        root_layout.addWidget(header)

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
        input_layout.addWidget(self.input_box)
        input_layout.addWidget(self.send_button)
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
        self.input_box.clear()
        response = self.chat_page.send_message(query)
        self.chat_history.append(f"用户：{query}")
        self.chat_history.append(f"助手：{response.answer}")

        self.sources_panel.clear()
        for source in response.sources:
            self.sources_panel.append(SourceCard(source).render_text())
            self.sources_panel.append("")

        self.tool_logs_panel.clear()
        for log in response.tool_logs:
            self.tool_log_panel.add_log(log)
        self.tool_logs_panel.setPlainText(self.tool_log_panel.render_text())
