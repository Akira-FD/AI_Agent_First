from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.main import bootstrap_application
from app.rag.ingest_pipeline import IngestPipeline
from app.ui.main_window import launch_pyqt_app


def main() -> None:
    app = bootstrap_application(ROOT)
    IngestPipeline(settings=app.settings, repository=app.repository).ingest_directory(app.settings.docs_dir)
    launch_pyqt_app(app.agent, app.settings, app.document_service, app.llm_service)


if __name__ == "__main__":
    main()
