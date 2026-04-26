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
            self.assertEqual(settings.llm_retry_attempts, 2)
            self.assertAlmostEqual(settings.llm_retry_backoff_seconds, 0.4)

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

    def test_reads_retry_configuration_from_environment(self) -> None:
        previous = {
            "AI_AGENT_FIRST_LLM_RETRY_ATTEMPTS": os.environ.get("AI_AGENT_FIRST_LLM_RETRY_ATTEMPTS"),
            "AI_AGENT_FIRST_LLM_RETRY_BACKOFF_SECONDS": os.environ.get("AI_AGENT_FIRST_LLM_RETRY_BACKOFF_SECONDS"),
        }
        os.environ["AI_AGENT_FIRST_LLM_RETRY_ATTEMPTS"] = "4"
        os.environ["AI_AGENT_FIRST_LLM_RETRY_BACKOFF_SECONDS"] = "1.25"
        try:
            settings = AppSettings.from_root(Path.cwd())
            self.assertEqual(settings.llm_retry_attempts, 4)
            self.assertAlmostEqual(settings.llm_retry_backoff_seconds, 1.25)
        finally:
            for key, value in previous.items():
                if value is None:
                    os.environ.pop(key, None)
                else:
                    os.environ[key] = value

        for key, value in previous.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value

    def test_reads_milvus_configuration_from_environment(self) -> None:
        previous = {
            "AI_AGENT_FIRST_MILVUS_ENABLED": os.environ.get("AI_AGENT_FIRST_MILVUS_ENABLED"),
            "AI_AGENT_FIRST_MILVUS_URI": os.environ.get("AI_AGENT_FIRST_MILVUS_URI"),
            "AI_AGENT_FIRST_MILVUS_COLLECTION": os.environ.get("AI_AGENT_FIRST_MILVUS_COLLECTION"),
            "AI_AGENT_FIRST_MILVUS_DIMENSION": os.environ.get("AI_AGENT_FIRST_MILVUS_DIMENSION"),
            "AI_AGENT_FIRST_MILVUS_LITE_PATH": os.environ.get("AI_AGENT_FIRST_MILVUS_LITE_PATH"),
        }
        os.environ["AI_AGENT_FIRST_MILVUS_ENABLED"] = "true"
        os.environ["AI_AGENT_FIRST_MILVUS_URI"] = "http://localhost:19530"
        os.environ["AI_AGENT_FIRST_MILVUS_COLLECTION"] = "ai_agent_first_chunks"
        os.environ["AI_AGENT_FIRST_MILVUS_DIMENSION"] = "96"
        os.environ["AI_AGENT_FIRST_MILVUS_LITE_PATH"] = "data/milvus/agent.db"
        try:
            with tempfile.TemporaryDirectory() as tmpdir:
                settings = AppSettings.from_root(Path(tmpdir))
                self.assertTrue(settings.milvus_enabled)
                self.assertEqual(settings.milvus_uri, "http://localhost:19530")
                self.assertEqual(settings.milvus_collection, "ai_agent_first_chunks")
                self.assertEqual(settings.milvus_dimension, 96)
                self.assertEqual(settings.milvus_lite_path.name, "agent.db")
        finally:
            for key, value in previous.items():
                if value is None:
                    os.environ.pop(key, None)
                else:
                    os.environ[key] = value

    def test_reads_retrieval_backend_configuration_from_environment(self) -> None:
        previous = {
            "AI_AGENT_FIRST_RETRIEVAL_BACKEND": os.environ.get("AI_AGENT_FIRST_RETRIEVAL_BACKEND"),
            "AI_AGENT_FIRST_EMBEDDING_BACKEND": os.environ.get("AI_AGENT_FIRST_EMBEDDING_BACKEND"),
            "AI_AGENT_FIRST_REMOTE_RETRIEVAL_URL": os.environ.get("AI_AGENT_FIRST_REMOTE_RETRIEVAL_URL"),
            "AI_AGENT_FIRST_RERANKER_BACKEND": os.environ.get("AI_AGENT_FIRST_RERANKER_BACKEND"),
            "AI_AGENT_FIRST_BGE_RERANKER_MODEL": os.environ.get("AI_AGENT_FIRST_BGE_RERANKER_MODEL"),
            "AI_AGENT_FIRST_RERANKER_PREFILTER_LIMIT": os.environ.get("AI_AGENT_FIRST_RERANKER_PREFILTER_LIMIT"),
        }
        os.environ["AI_AGENT_FIRST_RETRIEVAL_BACKEND"] = "milvus-lite"
        os.environ["AI_AGENT_FIRST_EMBEDDING_BACKEND"] = "hash"
        os.environ["AI_AGENT_FIRST_REMOTE_RETRIEVAL_URL"] = "http://127.0.0.1:9000/retrieve"
        os.environ["AI_AGENT_FIRST_RERANKER_BACKEND"] = "bge"
        os.environ["AI_AGENT_FIRST_BGE_RERANKER_MODEL"] = "BAAI/bge-reranker-v2-m3"
        os.environ["AI_AGENT_FIRST_RERANKER_PREFILTER_LIMIT"] = "6"
        try:
            with tempfile.TemporaryDirectory() as tmpdir:
                settings = AppSettings.from_root(Path(tmpdir))
                self.assertEqual(settings.retrieval_backend, "milvus-lite")
                self.assertEqual(settings.embedding_backend, "hash")
                self.assertEqual(settings.remote_retrieval_url, "http://127.0.0.1:9000/retrieve")
                self.assertEqual(settings.reranker_backend, "bge")
                self.assertEqual(settings.bge_reranker_model, "BAAI/bge-reranker-v2-m3")
                self.assertEqual(settings.reranker_prefilter_limit, 6)
        finally:
            for key, value in previous.items():
                if value is None:
                    os.environ.pop(key, None)
                else:
                    os.environ[key] = value

    def test_reads_bge_latency_tuning_configuration_from_environment(self) -> None:
        previous = {
            "AI_AGENT_FIRST_BGE_RERANKER_TEXT_MAX_CHARS": os.environ.get("AI_AGENT_FIRST_BGE_RERANKER_TEXT_MAX_CHARS"),
            "AI_AGENT_FIRST_BGE_RERANKER_BATCH_SIZE": os.environ.get("AI_AGENT_FIRST_BGE_RERANKER_BATCH_SIZE"),
            "AI_AGENT_FIRST_BGE_RERANKER_QUERY_MAX_LENGTH": os.environ.get("AI_AGENT_FIRST_BGE_RERANKER_QUERY_MAX_LENGTH"),
            "AI_AGENT_FIRST_BGE_RERANKER_MAX_LENGTH": os.environ.get("AI_AGENT_FIRST_BGE_RERANKER_MAX_LENGTH"),
            "AI_AGENT_FIRST_BGE_RERANKER_USE_FP16": os.environ.get("AI_AGENT_FIRST_BGE_RERANKER_USE_FP16"),
            "AI_AGENT_FIRST_BGE_RERANKER_DEVICES": os.environ.get("AI_AGENT_FIRST_BGE_RERANKER_DEVICES"),
        }
        os.environ["AI_AGENT_FIRST_BGE_RERANKER_TEXT_MAX_CHARS"] = "900"
        os.environ["AI_AGENT_FIRST_BGE_RERANKER_BATCH_SIZE"] = "12"
        os.environ["AI_AGENT_FIRST_BGE_RERANKER_QUERY_MAX_LENGTH"] = "48"
        os.environ["AI_AGENT_FIRST_BGE_RERANKER_MAX_LENGTH"] = "160"
        os.environ["AI_AGENT_FIRST_BGE_RERANKER_USE_FP16"] = "false"
        os.environ["AI_AGENT_FIRST_BGE_RERANKER_DEVICES"] = "cpu"
        try:
            with tempfile.TemporaryDirectory() as tmpdir:
                settings = AppSettings.from_root(Path(tmpdir))
                self.assertEqual(settings.bge_reranker_text_max_chars, 900)
                self.assertEqual(settings.bge_reranker_batch_size, 12)
                self.assertEqual(settings.bge_reranker_query_max_length, 48)
                self.assertEqual(settings.bge_reranker_max_length, 160)
                self.assertFalse(settings.bge_reranker_use_fp16)
                self.assertEqual(settings.bge_reranker_devices, "cpu")
        finally:
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
