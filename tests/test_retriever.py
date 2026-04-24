import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from app.models.document import DocumentChunk
from app.config.settings import AppSettings
from app.rag.ingest_pipeline import IngestPipeline
from app.rag.retriever import Retriever
from app.rag.vector_store import SearchMatch
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

    def test_can_retrieve_from_external_vector_store_port(self) -> None:
        class StubVectorStore:
            def __init__(self) -> None:
                self.queries = []

            def search(self, query: str, chunks, top_k: int):
                self.queries.append((query, top_k))
                selected = [chunk for chunk in chunks if "重启服务" in chunk.title or "重启服务" in " ".join(chunk.section_path)]
                return [type("SearchMatch", (), {"chunk": selected[0], "score": 9.5})()] if selected else []

        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            settings = AppSettings.from_root(root)
            (settings.docs_dir / "ops.md").write_text(SAMPLE_DOC, encoding="utf-8")

            repo = SQLiteRepository(settings.sqlite_path)
            IngestPipeline(settings=settings, repository=repo).ingest_directory(settings.docs_dir)
            vector_store = StubVectorStore()

            retriever = Retriever(repository=repo, top_k=3, vector_store=vector_store)
            result = retriever.retrieve("如何重启 redis 服务")

            self.assertEqual(vector_store.queries, [("如何重启 redis 服务", 6)])
            self.assertIn("重启服务", result.context_text)
            self.assertTrue(result.sources)

    def test_prefilters_candidates_before_expensive_reranker(self) -> None:
        class SpyVectorStore:
            def search(self, query: str, chunks, top_k: int):
                return [
                    SearchMatch(
                        chunk=DocumentChunk(
                            doc_id=str(index),
                            chunk_id=str(index),
                            title=title,
                            section_path=[title],
                            content=content,
                            source=f"{index}.md",
                            order=index,
                            token_count=10,
                        ),
                        score=10 - index,
                    )
                    for index, (title, content) in enumerate(
                        [
                            ("Redis timeout", "redis timeout should inspect slowlog and maxmemory"),
                            ("MySQL slow", "mysql slow query and explain"),
                            ("Redis memory", "redis oom maxmemory and memory policy"),
                            ("Kubernetes pod", "pod crashloop and kubectl describe"),
                            ("Redis latency", "redis latency doctor and networking"),
                            ("Nginx 502", "nginx upstream 502 bad gateway"),
                            ("Redis connection", "redis connection timeout and tcp backlog"),
                            ("Disk full", "linux disk full du df lsof"),
                        ],
                        start=1,
                    )
                ]

        class SpyReranker:
            def __init__(self) -> None:
                self.calls = []

            def backend_name(self) -> str:
                return "bge"

            def rerank(self, query: str, matches: list[SearchMatch], limit: int) -> list[SearchMatch]:
                self.calls.append({"query": query, "count": len(matches), "limit": limit})
                return matches[:limit]

        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            settings = AppSettings.from_root(root)
            repo = SQLiteRepository(settings.sqlite_path)
            reranker = SpyReranker()
            retriever = Retriever(
                repository=repo,
                top_k=5,
                vector_store=SpyVectorStore(),
                reranker=reranker,
                prefilter_limit=6,
            )

            retriever.retrieve("Redis timeout 怎么排查？")

            self.assertEqual(len(reranker.calls), 1)
            self.assertEqual(reranker.calls[0]["limit"], 5)
            self.assertEqual(reranker.calls[0]["count"], 6)

    def test_keeps_full_candidate_set_for_keyword_reranker(self) -> None:
        class StubVectorStore:
            def search(self, query: str, chunks, top_k: int):
                return [
                    SearchMatch(
                        chunk=DocumentChunk(
                            doc_id=str(index),
                            chunk_id=str(index),
                            title=f"Chunk {index}",
                            section_path=[f"Section {index}"],
                            content=f"redis timeout chunk {index}",
                            source=f"{index}.md",
                            order=index,
                            token_count=6,
                        ),
                        score=float(20 - index),
                    )
                    for index in range(8)
                ]

        class SpyKeywordReranker:
            def __init__(self) -> None:
                self.calls = []

            def backend_name(self) -> str:
                return "keyword-tech-weighted"

            def rerank(self, query: str, matches: list[SearchMatch], limit: int) -> list[SearchMatch]:
                self.calls.append(len(matches))
                return matches[:limit]

        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            settings = AppSettings.from_root(root)
            repo = SQLiteRepository(settings.sqlite_path)
            reranker = SpyKeywordReranker()
            retriever = Retriever(
                repository=repo,
                top_k=5,
                vector_store=StubVectorStore(),
                reranker=reranker,
                prefilter_limit=6,
            )

            retriever.retrieve("Redis timeout 怎么排查？")

            self.assertEqual(reranker.calls, [8])

    def test_records_stage_latency_breakdown_for_retrieval_pipeline(self) -> None:
        class StubVectorStore:
            def search(self, query: str, chunks, top_k: int):
                return [
                    SearchMatch(
                        chunk=DocumentChunk(
                            doc_id="1",
                            chunk_id="1",
                            title="Redis timeout",
                            section_path=["Redis", "Timeout"],
                            content="redis timeout should inspect slowlog and maxmemory",
                            source="redis.md",
                            order=0,
                            token_count=8,
                        ),
                        score=9.0,
                    )
                ]

        class StubReranker:
            def backend_name(self) -> str:
                return "bge"

            def rerank(self, query: str, matches: list[SearchMatch], limit: int) -> list[SearchMatch]:
                return matches[:limit]

        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            settings = AppSettings.from_root(root)
            repo = SQLiteRepository(settings.sqlite_path)
            retriever = Retriever(
                repository=repo,
                top_k=3,
                vector_store=StubVectorStore(),
                reranker=StubReranker(),
                prefilter_limit=3,
            )

            with patch(
                "app.rag.retriever.time.monotonic",
                side_effect=[1.0, 1.01, 1.01, 1.03, 1.03, 1.08, 1.08, 1.11],
            ):
                result = retriever.retrieve("Redis timeout 怎么排查？")

            self.assertEqual(result.stage_latency_ms["retrieval"], 10)
            self.assertEqual(result.stage_latency_ms["coarse_rerank"], 20)
            self.assertEqual(result.stage_latency_ms["bge_rerank"], 50)
            self.assertEqual(result.stage_latency_ms["context_build"], 30)


if __name__ == "__main__":
    unittest.main()
