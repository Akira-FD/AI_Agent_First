import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

import scripts.export_desktop_snapshot as export_desktop_snapshot
import scripts.run_desktop as run_desktop


class RunDesktopScriptTests(unittest.TestCase):
    def test_launches_desktop_with_llm_service(self) -> None:
        fake_app = SimpleNamespace(
            settings=SimpleNamespace(docs_dir="docs"),
            repository=object(),
            agent=object(),
            document_service=object(),
            llm_service=object(),
            vector_store=object(),
        )

        with (
            patch.object(run_desktop, "bootstrap_application", return_value=fake_app),
            patch.object(run_desktop, "IngestPipeline") as ingest_pipeline_cls,
            patch.object(run_desktop, "launch_pyqt_app") as launch_pyqt_app,
        ):
            run_desktop.main()

        ingest_pipeline_cls.assert_called_once_with(
            settings=fake_app.settings,
            repository=fake_app.repository,
            vector_indexer=fake_app.vector_store,
        )
        launch_pyqt_app.assert_called_once_with(
            fake_app.agent,
            fake_app.settings,
            fake_app.document_service,
            fake_app.llm_service,
        )

    def test_exports_desktop_snapshot_with_demo_state(self) -> None:
        fake_window = SimpleNamespace(
            apply_startup_geometry=lambda *args, **kwargs: None,
            center_on_screen=lambda *args, **kwargs: None,
            show=lambda: None,
            load_demo_state=lambda: None,
            export_snapshot=lambda path: True,
        )
        fake_app = SimpleNamespace(
            settings=SimpleNamespace(docs_dir="docs"),
            repository=object(),
            agent=object(),
            document_service=object(),
            llm_service=object(),
            vector_store=object(),
        )
        fake_qapp = SimpleNamespace(
            primaryScreen=lambda: None,
            processEvents=lambda: None,
        )

        with (
            patch.object(export_desktop_snapshot, "bootstrap_application", return_value=fake_app),
            patch.object(export_desktop_snapshot, "IngestPipeline") as ingest_pipeline_cls,
            patch.object(export_desktop_snapshot, "MainWindow", return_value=fake_window) as main_window_cls,
            patch.object(export_desktop_snapshot, "QApplication") as qapplication_cls,
        ):
            qapplication_cls.instance.return_value = fake_qapp
            output = export_desktop_snapshot.export_snapshot(Path("demo.png"))

        self.assertEqual(output, Path("demo.png"))
        ingest_pipeline_cls.assert_called_once_with(
            settings=fake_app.settings,
            repository=fake_app.repository,
            vector_indexer=fake_app.vector_store,
        )
        main_window_cls.assert_called_once_with(
            agent=fake_app.agent,
            settings=fake_app.settings,
            document_service=fake_app.document_service,
            llm_service=fake_app.llm_service,
        )


if __name__ == "__main__":
    unittest.main()
