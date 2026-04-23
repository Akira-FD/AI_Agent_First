import tempfile
import unittest
from pathlib import Path

from app.config.settings import AppSettings
from app.rag.ingest_pipeline import IngestPipeline
from app.rag.retriever import Retriever
from app.repositories.sqlite_repo import SQLiteRepository


SAMPLE_DOC = """# Redis 运维手册

## 查看状态

使用 systemctl status redis 查看运行状态。

## 重启服务

使用 systemctl restart redis 完成服务重启。
"""


class RetrieverTests(unittest.TestCase):
    def test_returns_context_and_sources_for_query(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            settings = AppSettings.from_root(root)
            (settings.docs_dir / "ops.md").write_text(SAMPLE_DOC, encoding="utf-8")

            repo = SQLiteRepository(settings.sqlite_path)
            IngestPipeline(settings=settings, repository=repo).ingest_directory(settings.docs_dir)

            retriever = Retriever(repository=repo, top_k=3)
            result = retriever.retrieve("如何重启 redis 服务")

            self.assertTrue(result.context_text)
            self.assertGreaterEqual(len(result.sources), 1)
            self.assertIn("重启服务", result.context_text)
            self.assertIn("score", result.sources[0])
            self.assertIn("excerpt", result.sources[0])
            self.assertGreater(float(result.sources[0]["score"]), 0)

    def test_limits_context_length_for_ui_and_llm_consumption(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            settings = AppSettings.from_root(root)
            long_doc = "# Redis\n\n## 重启服务\n\n" + " ".join(["redis 重启 验证"] * 80)
            (settings.docs_dir / "long.md").write_text(long_doc, encoding="utf-8")

            repo = SQLiteRepository(settings.sqlite_path)
            IngestPipeline(settings=settings, repository=repo).ingest_directory(settings.docs_dir)

            retriever = Retriever(repository=repo, top_k=5, max_context_chars=120)
            result = retriever.retrieve("redis 重启")

            self.assertLessEqual(len(result.context_text), 120)
            self.assertTrue(result.sources)


if __name__ == "__main__":
    unittest.main()
