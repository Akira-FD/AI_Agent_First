import json
import os
import unittest
from pathlib import Path
from http.client import RemoteDisconnected
from unittest.mock import patch

from app.config.settings import AppSettings
from app.main import bootstrap_application
from app.services.llm_service import OpenAICompatibleLLMService, build_llm_service
from app.ui.main_window import DesktopAppShell


class FakeRequester:
    def __init__(self, payload: dict | None = None, error: Exception | None = None) -> None:
        self.payload = payload or {
            "choices": [
                {
                    "message": {
                        "content": "建议先检查 maxmemory、slowlog 和连接数，再决定是否重启。"
                    }
                }
            ]
        }
        self.error = error
        self.calls: list[dict[str, object]] = []

    def __call__(self, *, url: str, headers: dict[str, str], payload: dict[str, object], timeout: int) -> dict:
        self.calls.append(
            {
                "url": url,
                "headers": headers,
                "payload": payload,
                "timeout": timeout,
            }
        )
        if self.error:
            raise self.error
        return self.payload


class SequencedRequester:
    def __init__(self, outcomes: list[object]) -> None:
        self.outcomes = list(outcomes)
        self.calls: list[dict[str, object]] = []

    def __call__(self, *, url: str, headers: dict[str, str], payload: dict[str, object], timeout: int) -> dict:
        self.calls.append(
            {
                "url": url,
                "headers": headers,
                "payload": payload,
                "timeout": timeout,
            }
        )
        outcome = self.outcomes[len(self.calls) - 1]
        if isinstance(outcome, Exception):
            raise outcome
        return outcome


class RealLLMIntegrationTests(unittest.TestCase):
    def test_settings_load_real_llm_configuration_from_environment(self) -> None:
        previous = {
            "AI_AGENT_FIRST_LLM_API_KEY": os.environ.get("AI_AGENT_FIRST_LLM_API_KEY"),
            "AI_AGENT_FIRST_LLM_BASE_URL": os.environ.get("AI_AGENT_FIRST_LLM_BASE_URL"),
            "AI_AGENT_FIRST_LLM_MODEL": os.environ.get("AI_AGENT_FIRST_LLM_MODEL"),
        }
        os.environ["AI_AGENT_FIRST_LLM_API_KEY"] = "test-key"
        os.environ["AI_AGENT_FIRST_LLM_BASE_URL"] = "https://example.com/v1"
        os.environ["AI_AGENT_FIRST_LLM_MODEL"] = "test-model"
        try:
            with patch("app.config.settings._read_local_env_file", return_value={}):
                settings = AppSettings.from_root(Path.cwd())
            self.assertEqual(settings.llm_api_key, "test-key")
            self.assertEqual(settings.llm_base_url, "https://example.com/v1")
            self.assertEqual(settings.llm_model, "test-model")
        finally:
            for key, value in previous.items():
                if value is None:
                    os.environ.pop(key, None)
                else:
                    os.environ[key] = value

    def test_openai_compatible_service_builds_chat_completion_request(self) -> None:
        requester = FakeRequester()
        service = OpenAICompatibleLLMService(
            api_key="test-key",
            base_url="https://example.com/v1",
            model="demo-model",
            requester=requester,
        )

        answer = service.generate_answer(
            user_query="Redis OOM 时先看什么？",
            context_text="建议先检查 maxmemory、slowlog 和连接数。",
        )

        self.assertIn("maxmemory", answer)
        self.assertEqual(len(requester.calls), 1)
        call = requester.calls[0]
        self.assertEqual(call["url"], "https://example.com/v1/chat/completions")
        self.assertEqual(call["headers"]["Authorization"], "Bearer test-key")
        self.assertEqual(call["payload"]["model"], "demo-model")
        self.assertIn("Redis OOM", json.dumps(call["payload"], ensure_ascii=False))

    def test_builder_falls_back_to_rule_based_service_when_remote_call_fails(self) -> None:
        service = build_llm_service(
            settings=type(
                "Settings",
                (),
                {
                    "llm_api_key": "test-key",
                    "llm_base_url": "https://example.com/v1",
                    "llm_model": "demo-model",
                    "llm_timeout_seconds": 15,
                    "llm_retry_attempts": 2,
                    "llm_retry_backoff_seconds": 0,
                },
            )(),
            requester=FakeRequester(error=RuntimeError("network down")),
        )

        answer = service.generate_answer(
            user_query="Redis 连接失败时先看什么？",
            context_text="建议先检查进程、端口和资源占用情况。",
        )

        self.assertIn("进程", answer)
        self.assertNotIn("network down", answer)

    def test_retries_timeout_once_then_returns_remote_answer(self) -> None:
        requester = SequencedRequester(
            [
                TimeoutError("timed out"),
                {"choices": [{"message": {"content": "请先检查 maxmemory、内存碎片率和淘汰策略。"}}]},
            ]
        )
        service = OpenAICompatibleLLMService(
            api_key="test-key",
            base_url="https://relay.example.com/v1",
            model="gpt-5.2",
            requester=requester,
            retry_attempts=2,
            retry_backoff_seconds=0,
        )

        answer = service.generate_answer(
            user_query="Redis OOM 时应该优先检查哪些指标和配置？",
            context_text="建议优先检查 maxmemory、内存碎片率和淘汰策略。",
        )

        self.assertEqual(len(requester.calls), 2)
        self.assertIn("maxmemory", answer)
        self.assertNotIn("根据知识库", answer)

    def test_retries_remote_disconnect_once_then_returns_remote_answer(self) -> None:
        requester = SequencedRequester(
            [
                RemoteDisconnected("Remote end closed connection without response"),
                {"choices": [{"message": {"content": "先看 error log、wait_timeout、网络抖动和连接池参数。"}}]},
            ]
        )
        service = OpenAICompatibleLLMService(
            api_key="test-key",
            base_url="https://relay.example.com/v1",
            model="gpt-5.2",
            requester=requester,
            retry_attempts=2,
            retry_backoff_seconds=0,
        )

        answer = service.generate_answer(
            user_query="MySQL aborted connection 通常先怎么排查？",
            context_text="建议先看 error log、wait_timeout、网络抖动和连接池参数。",
        )

        self.assertEqual(len(requester.calls), 2)
        self.assertIn("wait_timeout", answer)
        self.assertNotIn("根据知识库", answer)

    def test_does_not_retry_http_error_and_falls_back_immediately(self) -> None:
        requester = SequencedRequester([RuntimeError("LLM request failed with HTTP 401")])
        service = OpenAICompatibleLLMService(
            api_key="test-key",
            base_url="https://relay.example.com/v1",
            model="gpt-5.2",
            requester=requester,
            retry_attempts=3,
            retry_backoff_seconds=0,
        )

        answer = service.generate_answer(
            user_query="Redis 连接失败时先看什么？",
            context_text="建议先检查进程、端口和资源占用情况。",
        )

        self.assertEqual(len(requester.calls), 1)
        self.assertIn("进程", answer)

    def test_answer_result_exposes_timeout_diagnostics_after_retry_exhaustion(self) -> None:
        requester = SequencedRequester([TimeoutError("timed out"), TimeoutError("timed out")])
        service = OpenAICompatibleLLMService(
            api_key="test-key",
            base_url="https://relay.example.com/v1",
            model="gpt-5.2",
            requester=requester,
            retry_attempts=2,
            retry_backoff_seconds=0,
        )

        result = service.generate_answer_result(
            user_query="Redis OOM 时应该优先检查哪些指标和配置？",
            context_text="建议优先检查 maxmemory、内存碎片率和淘汰策略。",
        )

        self.assertEqual(result.answer_backend, "fallback")
        self.assertEqual(result.provider_status, "timeout")
        self.assertEqual(result.provider_attempts, 2)
        self.assertIn("timed out", result.provider_error)

    def test_answer_result_exposes_disconnect_diagnostics_after_retry_exhaustion(self) -> None:
        requester = SequencedRequester(
            [
                RemoteDisconnected("Remote end closed connection without response"),
                RemoteDisconnected("Remote end closed connection without response"),
            ]
        )
        service = OpenAICompatibleLLMService(
            api_key="test-key",
            base_url="https://relay.example.com/v1",
            model="gpt-5.2",
            requester=requester,
            retry_attempts=2,
            retry_backoff_seconds=0,
        )

        result = service.generate_answer_result(
            user_query="MySQL aborted connection 通常先怎么排查？",
            context_text="建议先看 error log、wait_timeout、网络抖动和连接池参数。",
        )

        self.assertEqual(result.answer_backend, "fallback")
        self.assertEqual(result.provider_status, "disconnect")
        self.assertEqual(result.provider_attempts, 2)

    def test_answer_result_exposes_http_status_code_diagnostics(self) -> None:
        requester = SequencedRequester([RuntimeError("LLM request failed with HTTP 429")])
        service = OpenAICompatibleLLMService(
            api_key="test-key",
            base_url="https://relay.example.com/v1",
            model="gpt-5.2",
            requester=requester,
            retry_attempts=3,
            retry_backoff_seconds=0,
        )

        result = service.generate_answer_result(
            user_query="Kubernetes Pod 反复 CrashLoopBackOff 怎么排查？",
            context_text="建议先看 describe 和 previous logs。",
        )

        self.assertEqual(result.answer_backend, "fallback")
        self.assertEqual(result.provider_status, "http_429")
        self.assertEqual(result.provider_attempts, 1)

    def test_answer_result_marks_provider_success(self) -> None:
        requester = SequencedRequester(
            [{"choices": [{"message": {"content": "先看 describe、events 和 previous logs。"}}]}]
        )
        service = OpenAICompatibleLLMService(
            api_key="test-key",
            base_url="https://relay.example.com/v1",
            model="gpt-5.2",
            requester=requester,
        )

        result = service.generate_answer_result(
            user_query="Kubernetes Pod 反复 CrashLoopBackOff 怎么排查？",
            context_text="建议先看 describe 和 previous logs。",
        )

        self.assertEqual(result.answer_backend, "remote")
        self.assertEqual(result.provider_status, "success")
        self.assertEqual(result.provider_attempts, 1)

    def test_bootstrap_uses_real_llm_service_when_api_key_exists(self) -> None:
        previous = {
            "AI_AGENT_FIRST_LLM_API_KEY": os.environ.get("AI_AGENT_FIRST_LLM_API_KEY"),
            "AI_AGENT_FIRST_LLM_MODEL": os.environ.get("AI_AGENT_FIRST_LLM_MODEL"),
        }
        os.environ["AI_AGENT_FIRST_LLM_API_KEY"] = "test-key"
        os.environ["AI_AGENT_FIRST_LLM_MODEL"] = "demo-model"
        try:
            with patch("app.config.settings._read_local_env_file", return_value={}):
                app = bootstrap_application(Path.cwd())
            self.assertIsInstance(app.llm_service, OpenAICompatibleLLMService)
            self.assertIn("demo-model", app.ui_shell.render_status())
            self.assertEqual(app.settings.llm_retry_attempts, 2)
        finally:
            for key, value in previous.items():
                if value is None:
                    os.environ.pop(key, None)
                else:
                    os.environ[key] = value

    def test_builder_passes_retry_configuration_to_real_llm_service(self) -> None:
        service = build_llm_service(
            settings=type(
                "Settings",
                (),
                {
                    "llm_api_key": "test-key",
                    "llm_base_url": "https://example.com/v1",
                    "llm_model": "demo-model",
                    "llm_timeout_seconds": 15,
                    "llm_retry_attempts": 4,
                    "llm_retry_backoff_seconds": 1.5,
                },
            )(),
            requester=FakeRequester(),
        )

        self.assertEqual(service.retry_attempts, 4)
        self.assertAlmostEqual(service.retry_backoff_seconds, 1.5)

    def test_status_mentions_missing_api_key_when_model_is_configured(self) -> None:
        settings = AppSettings.from_root(Path.cwd())
        shell = DesktopAppShell(
            agent=object(),
            settings=type(
                "Settings",
                (),
                {
                    "app_name": settings.app_name,
                    "docs_dir": settings.docs_dir,
                    "llm_api_key": "",
                    "llm_base_url": "https://api.openai.com/v1",
                    "llm_model": "gpt-5.2",
                },
            )(),
            llm_service=type("Fallback", (), {"backend_label": lambda self: "local-rule-based-fallback"})(),
        )

        status = shell.render_status()

        self.assertIn("local-rule-based-fallback", status)
        self.assertIn("OPENAI_API_KEY", status)
        self.assertIn("gpt-5.2", status)


if __name__ == "__main__":
    unittest.main()
