from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from app.agent.graph import MVPAgent
from app.config.settings import AppSettings
from app.repositories.sqlite_repo import SQLiteRepository
from app.services.document_service import DocumentService
from app.services.llm_service import RuleBasedLLMService
from app.services.session_service import SessionService
from app.tools.registry import ToolRegistry
from app.ui.main_window import DesktopAppShell


@dataclass
class BootstrappedApplication:
    settings: AppSettings
    repository: SQLiteRepository
    session_service: SessionService
    document_service: DocumentService
    llm_service: RuleBasedLLMService
    tool_registry: ToolRegistry
    agent: MVPAgent
    ui_shell: DesktopAppShell


def bootstrap_application(root: Path | None = None) -> BootstrappedApplication:
    workspace_root = (root or Path(__file__).resolve().parents[1]).resolve()
    settings = AppSettings.from_root(workspace_root)
    repository = SQLiteRepository(settings.sqlite_path)
    session_service = SessionService()
    document_service = DocumentService(repository)
    llm_service = RuleBasedLLMService()
    tool_registry = ToolRegistry.with_defaults()
    agent = MVPAgent(
        settings=settings,
        repository=repository,
        session_service=session_service,
        document_service=document_service,
        llm_service=llm_service,
        tool_registry=tool_registry,
    )
    ui_shell = DesktopAppShell(agent=agent, settings=settings)
    return BootstrappedApplication(
        settings=settings,
        repository=repository,
        session_service=session_service,
        document_service=document_service,
        llm_service=llm_service,
        tool_registry=tool_registry,
        agent=agent,
        ui_shell=ui_shell,
    )


def main() -> None:
    app = bootstrap_application()
    print(app.ui_shell.render_status())


if __name__ == "__main__":
    main()
