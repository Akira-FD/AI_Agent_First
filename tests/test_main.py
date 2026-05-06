import tempfile
import unittest
from pathlib import Path
import os

from app.main import bootstrap_application


class MainBootstrapTests(unittest.TestCase):
    def test_bootstrap_builds_runtime_services(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            app = bootstrap_application(Path(tmpdir))

            self.assertIsNotNone(app.settings)
            self.assertIsNotNone(app.agent)
            self.assertTrue(app.settings.docs_dir.exists())

    def test_bootstrap_uses_configured_remote_retrieval_backend(self) -> None:
        previous = {
            "AI_AGENT_FIRST_RETRIEVAL_BACKEND": os.environ.get("AI_AGENT_FIRST_RETRIEVAL_BACKEND"),
            "AI_AGENT_FIRST_REMOTE_RETRIEVAL_URL": os.environ.get("AI_AGENT_FIRST_REMOTE_RETRIEVAL_URL"),
        }
        os.environ["AI_AGENT_FIRST_RETRIEVAL_BACKEND"] = "remote"
        os.environ["AI_AGENT_FIRST_REMOTE_RETRIEVAL_URL"] = "http://127.0.0.1:9000/retrieve"
        try:
            with tempfile.TemporaryDirectory() as tmpdir:
                app = bootstrap_application(Path(tmpdir))

                self.assertEqual(app.settings.retrieval_backend, "remote")
                self.assertEqual(app.vector_store.__class__.__name__, "RemoteVectorStore")
                self.assertEqual(app.agent.retriever.vector_store.__class__.__name__, "RemoteVectorStore")
        finally:
            for key, value in previous.items():
                if value is None:
                    os.environ.pop(key, None)
                else:
                    os.environ[key] = value

    def test_bootstrap_applies_recent_message_limit_from_settings(self) -> None:
        previous = os.environ.get("AI_AGENT_FIRST_RECENT_MESSAGE_LIMIT")
        os.environ["AI_AGENT_FIRST_RECENT_MESSAGE_LIMIT"] = "3"
        try:
            with tempfile.TemporaryDirectory() as tmpdir:
                app = bootstrap_application(Path(tmpdir))

                self.assertEqual(app.settings.recent_message_limit, 3)
                self.assertEqual(app.session_service.recent_limit, 3)
        finally:
            if previous is None:
                os.environ.pop("AI_AGENT_FIRST_RECENT_MESSAGE_LIMIT", None)
            else:
                os.environ["AI_AGENT_FIRST_RECENT_MESSAGE_LIMIT"] = previous


if __name__ == "__main__":
    unittest.main()
