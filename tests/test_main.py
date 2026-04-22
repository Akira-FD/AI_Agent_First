import tempfile
import unittest
from pathlib import Path

from app.main import bootstrap_application


class MainBootstrapTests(unittest.TestCase):
    def test_bootstrap_builds_runtime_services(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            app = bootstrap_application(Path(tmpdir))

            self.assertIsNotNone(app.settings)
            self.assertIsNotNone(app.agent)
            self.assertTrue(app.settings.docs_dir.exists())


if __name__ == "__main__":
    unittest.main()
