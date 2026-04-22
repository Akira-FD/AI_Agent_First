import os
import tempfile
import unittest
from pathlib import Path

from app.config.settings import AppSettings


class SettingsTests(unittest.TestCase):
    def test_loads_defaults_and_creates_runtime_directories(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            settings = AppSettings.from_root(root)

            self.assertEqual(settings.app_name, "AI Agent First")
            self.assertTrue(settings.data_dir.exists())
            self.assertTrue(settings.docs_dir.exists())
            self.assertTrue(settings.sqlite_path.parent.exists())

    def test_reads_environment_overrides(self) -> None:
        previous = os.environ.get("AI_AGENT_FIRST_TOP_K")
        os.environ["AI_AGENT_FIRST_TOP_K"] = "7"
        try:
            settings = AppSettings.from_root(Path.cwd())
            self.assertEqual(settings.retrieval_top_k, 7)
        finally:
            if previous is None:
                os.environ.pop("AI_AGENT_FIRST_TOP_K", None)
            else:
                os.environ["AI_AGENT_FIRST_TOP_K"] = previous


if __name__ == "__main__":
    unittest.main()
