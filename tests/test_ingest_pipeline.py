import tempfile
import unittest
from pathlib import Path

from app.config.settings import AppSettings
from app.models.document import DocumentRecord
from app.rag.ingest_pipeline import IngestPipeline
from app.repositories.sqlite_repo import SQLiteRepository


SAMPLE_DOC = """# Redis 故障排查

## 服务状态

如果 Redis 服务异常，请先检查进程状态和端口监听。

## 常见恢复步骤

1. 检查日志
2. 重启服务
3. 验证健康状态
"""


class IngestPipelineTests(unittest.TestCase):
    def test_ingests_markdown_into_sqlite_and_memory_store(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            settings = AppSettings.from_root(root)
            sample_path = settings.docs_dir / "redis.md"
            sample_path.write_text(SAMPLE_DOC, encoding="utf-8")

            repo = SQLiteRepository(settings.sqlite_path)
            pipeline = IngestPipeline(settings=settings, repository=repo)

            result = pipeline.ingest_directory(settings.docs_dir)

            self.assertEqual(result.document_count, 1)
            self.assertGreaterEqual(result.chunk_count, 2)
            stored_docs = repo.list_documents()
            stored_chunks = repo.list_chunks()
            self.assertEqual(len(stored_docs), 1)
            self.assertEqual(len(stored_chunks), result.chunk_count)

    def test_reingest_is_idempotent_for_same_markdown_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            settings = AppSettings.from_root(root)
            sample_path = settings.docs_dir / "redis.md"
            sample_path.write_text(SAMPLE_DOC, encoding="utf-8")

            repo = SQLiteRepository(settings.sqlite_path)
            pipeline = IngestPipeline(settings=settings, repository=repo)

            first = pipeline.ingest_directory(settings.docs_dir)
            second = pipeline.ingest_directory(settings.docs_dir)

            self.assertEqual(first.document_count, 1)
            self.assertEqual(second.document_count, 1)
            self.assertEqual(len(repo.list_documents()), 1)
            self.assertEqual(len(repo.list_chunks()), first.chunk_count)

    def test_ingest_cleans_up_legacy_duplicates_with_same_path(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            settings = AppSettings.from_root(root)
            sample_path = settings.docs_dir / "redis.md"
            sample_path.write_text(SAMPLE_DOC, encoding="utf-8")

            repo = SQLiteRepository(settings.sqlite_path)
            repo.upsert_document(
                DocumentRecord(
                    id="legacy-doc",
                    title="legacy",
                    source=sample_path.name,
                    path=str(sample_path),
                )
            )
            repo.replace_document_chunks(
                "legacy-doc",
                [],
            )

            pipeline = IngestPipeline(settings=settings, repository=repo)
            pipeline.ingest_directory(settings.docs_dir)

            self.assertEqual(len(repo.list_documents()), 1)


if __name__ == "__main__":
    unittest.main()
