import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

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

    def test_runtime_script_uses_lightweight_settings_and_llm_validation(self) -> None:
        from scripts import validate_runtime as runtime_script

        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            llm_service = RuleBasedLLMService()

            with patch.object(runtime_script, "ROOT", root):
                with patch.object(runtime_script, "AppSettings", wraps=AppSettings) as settings_cls:
                    with patch.object(runtime_script, "build_llm_service", return_value=llm_service) as build_llm:
                        with patch.object(runtime_script, "validate_runtime_capabilities") as validate_runtime:
                            validate_runtime.return_value = {"ok": True}
                            runtime_script.main()

            settings_cls.from_root.assert_called_once_with(root)
            build_llm.assert_called_once()
            validate_runtime.assert_called_once()


if __name__ == "__main__":
    unittest.main()
