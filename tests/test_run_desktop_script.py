import unittest
from types import SimpleNamespace
from unittest.mock import patch

import scripts.run_desktop as run_desktop


class RunDesktopScriptTests(unittest.TestCase):
    def test_launches_desktop_with_llm_service(self) -> None:
        fake_app = SimpleNamespace(
            settings=SimpleNamespace(docs_dir="docs"),
            repository=object(),
            agent=object(),
            document_service=object(),
            llm_service=object(),
        )

        with (
            patch.object(run_desktop, "bootstrap_application", return_value=fake_app),
            patch.object(run_desktop, "IngestPipeline") as ingest_pipeline_cls,
            patch.object(run_desktop, "launch_pyqt_app") as launch_pyqt_app,
        ):
            run_desktop.main()

        ingest_pipeline_cls.assert_called_once()
        launch_pyqt_app.assert_called_once_with(
            fake_app.agent,
            fake_app.settings,
            fake_app.document_service,
            fake_app.llm_service,
        )


if __name__ == "__main__":
    unittest.main()
