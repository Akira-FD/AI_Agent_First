import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from app.config.settings import AppSettings, _read_windows_persistent_env


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

    def test_reads_llm_configuration_from_dotenv_file(self) -> None:
        previous = {
            "AI_AGENT_FIRST_LLM_API_KEY": os.environ.get("AI_AGENT_FIRST_LLM_API_KEY"),
            "AI_AGENT_FIRST_LLM_BASE_URL": os.environ.get("AI_AGENT_FIRST_LLM_BASE_URL"),
            "AI_AGENT_FIRST_LLM_MODEL": os.environ.get("AI_AGENT_FIRST_LLM_MODEL"),
        }
        for key in previous:
            os.environ.pop(key, None)

        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / ".env").write_text(
                "\n".join(
                    [
                        "AI_AGENT_FIRST_LLM_API_KEY=test-key",
                        "AI_AGENT_FIRST_LLM_BASE_URL=https://api.openai.com/v1",
                        "AI_AGENT_FIRST_LLM_MODEL=gpt-5.2",
                    ]
                ),
                encoding="utf-8",
            )

            settings = AppSettings.from_root(root)

            self.assertEqual(settings.llm_api_key, "test-key")
            self.assertEqual(settings.llm_base_url, "https://api.openai.com/v1")
            self.assertEqual(settings.llm_model, "gpt-5.2")

        for key, value in previous.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value

    def test_dotenv_llm_configuration_overrides_stale_process_environment(self) -> None:
        previous = {
            "AI_AGENT_FIRST_LLM_BASE_URL": os.environ.get("AI_AGENT_FIRST_LLM_BASE_URL"),
            "AI_AGENT_FIRST_LLM_MODEL": os.environ.get("AI_AGENT_FIRST_LLM_MODEL"),
        }
        os.environ["AI_AGENT_FIRST_LLM_BASE_URL"] = "https://api.openai.com/v1"
        os.environ["AI_AGENT_FIRST_LLM_MODEL"] = "gpt-4.1-mini"

        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / ".env").write_text(
                "\n".join(
                    [
                        "AI_AGENT_FIRST_LLM_BASE_URL=https://api1.oai1.online/v1",
                        "AI_AGENT_FIRST_LLM_MODEL=gpt-5.2",
                    ]
                ),
                encoding="utf-8",
            )

            settings = AppSettings.from_root(root)

            self.assertEqual(settings.llm_base_url, "https://api1.oai1.online/v1")
            self.assertEqual(settings.llm_model, "gpt-5.2")

        for key, value in previous.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value

    def test_reads_llm_configuration_from_windows_persistent_env_when_process_env_is_empty(self) -> None:
        previous = {
            "AI_AGENT_FIRST_LLM_API_KEY": os.environ.get("AI_AGENT_FIRST_LLM_API_KEY"),
            "AI_AGENT_FIRST_LLM_BASE_URL": os.environ.get("AI_AGENT_FIRST_LLM_BASE_URL"),
            "AI_AGENT_FIRST_LLM_MODEL": os.environ.get("AI_AGENT_FIRST_LLM_MODEL"),
            "OPENAI_API_KEY": os.environ.get("OPENAI_API_KEY"),
        }
        for key in previous:
            os.environ.pop(key, None)

        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            with patch(
                "app.config.settings._read_windows_persistent_env",
                return_value={
                    "OPENAI_API_KEY": "persisted-key",
                    "AI_AGENT_FIRST_LLM_BASE_URL": "https://api.openai.com/v1",
                    "AI_AGENT_FIRST_LLM_MODEL": "gpt-5.2",
                },
            ):
                settings = AppSettings.from_root(root)

            self.assertEqual(settings.llm_api_key, "persisted-key")
            self.assertEqual(settings.llm_base_url, "https://api.openai.com/v1")
            self.assertEqual(settings.llm_model, "gpt-5.2")

        for key, value in previous.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value


if __name__ == "__main__":
    unittest.main()
