import tempfile
import unittest
from pathlib import Path

from app.config.settings import AppSettings
from app.services.llm_service import OpenAICompatibleLLMService, RuleBasedLLMService
from app.validation.runtime_validation import validate_runtime_capabilities


class RuntimeValidationTests(unittest.TestCase):
    def test_reports_local_fallback_when_api_key_missing(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            settings = AppSettings.from_root(Path(tmpdir))
            llm_service = RuleBasedLLMService()

            report = validate_runtime_capabilities(settings=settings, llm_service=llm_service)

            self.assertTrue(report["docs_dir_ready"])
            self.assertTrue(report["sqlite_dir_ready"])
            self.assertEqual(report["llm_backend"], "local-rule-based-fallback")
            self.assertFalse(report["llm_remote_configured"])
            self.assertFalse(report["llm_sse_supported"])

    def test_reports_remote_llm_and_sse_support_when_openai_compatible_is_configured(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            settings = AppSettings.from_root(Path(tmpdir))
            llm_service = OpenAICompatibleLLMService(
                api_key="test-key",
                base_url="https://example.com/v1",
                model="gpt-5.2",
                requester=lambda **kwargs: {"choices": [{"message": {"content": "ok"}}]},
                stream_requester=lambda **kwargs: iter([b"data: [DONE]\n\n"]),
            )

            report = validate_runtime_capabilities(settings=settings, llm_service=llm_service)

            self.assertEqual(report["llm_backend"], "openai-compatible:gpt-5.2")
            self.assertTrue(report["llm_remote_configured"])
            self.assertTrue(report["llm_sse_supported"])


if __name__ == "__main__":
    unittest.main()
