from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import argparse

from app.agent.graph import MVPAgent
from app.config.settings import AppSettings
from app.rag.factory import build_retriever
from app.repositories.sqlite_repo import SQLiteRepository
from app.services.document_service import DocumentService
from app.services.llm_service import build_llm_service
from app.services.session_service import SessionService
from app.tools.registry import ToolRegistry
from app.ui.main_window import DesktopAppShell, launch_pyqt_app


@dataclass
class BootstrappedApplication:
    settings: AppSettings
    repository: SQLiteRepository
    session_service: SessionService
    document_service: DocumentService
    llm_service: object
    tool_registry: ToolRegistry
    vector_store: object
    agent: MVPAgent
    ui_shell: DesktopAppShell


def bootstrap_application(root: Path | None = None) -> BootstrappedApplication:
    workspace_root = (root or Path(__file__).resolve().parents[1]).resolve()
    settings = AppSettings.from_root(workspace_root)
    repository = SQLiteRepository(settings.sqlite_path)
    session_service = SessionService()
    document_service = DocumentService(repository)
    llm_service = build_llm_service(settings)
    tool_registry = ToolRegistry.with_defaults()
    retriever = build_retriever(settings=settings, repository=repository)
    vector_store = retriever.vector_store
    agent = MVPAgent(
        settings=settings,
        repository=repository,
        session_service=session_service,
        document_service=document_service,
        llm_service=llm_service,
        tool_registry=tool_registry,
        retriever=retriever,
        vector_store=vector_store,
    )
    ui_shell = DesktopAppShell(
        agent=agent,
        settings=settings,
        document_service=document_service,
        llm_service=llm_service,
    )
    return BootstrappedApplication(
        settings=settings,
        repository=repository,
        session_service=session_service,
        document_service=document_service,
        llm_service=llm_service,
        tool_registry=tool_registry,
        vector_store=vector_store,
        agent=agent,
        ui_shell=ui_shell,
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="AI Agent First local MVP")
    parser.add_argument("--ui", action="store_true", help="Launch the PyQt6 desktop UI.")
    args = parser.parse_args()

    app = bootstrap_application()
    if args.ui:
        launch_pyqt_app(app.agent, app.settings, app.document_service, app.llm_service)
        return
    print(app.ui_shell.render_status())


if __name__ == "__main__":
    main()
