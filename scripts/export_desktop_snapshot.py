from __future__ import annotations
# ruff: noqa: E402

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.main import bootstrap_application
from app.rag.ingest_pipeline import IngestPipeline
from app.ui.main_window import MainWindow, QApplication


def export_snapshot(output_path: Path) -> Path:
    if QApplication is None:
        raise RuntimeError("PyQt6 is not installed. Run `pip install PyQt6` before exporting a desktop snapshot.")

    app = QApplication.instance() or QApplication([])
    boot = bootstrap_application(ROOT)
    IngestPipeline(
        settings=boot.settings,
        repository=boot.repository,
        vector_indexer=boot.vector_store,
    ).ingest_directory(boot.settings.docs_dir)
    window = MainWindow(
        agent=boot.agent,
        settings=boot.settings,
        document_service=boot.document_service,
        llm_service=boot.llm_service,
    )
    window.apply_startup_geometry(app.primaryScreen())
    window.center_on_screen(app.primaryScreen())
    window.load_demo_state()
    window.show()
    app.processEvents()
    if not window.export_snapshot(output_path):
        raise RuntimeError(f"Failed to export desktop snapshot to {output_path}")
    if hasattr(window, "close"):
        window.close()
    return output_path


def main() -> None:
    target = ROOT / "results" / "desktop_snapshot.png"
    exported = export_snapshot(target)
    print(exported)


if __name__ == "__main__":
    main()
