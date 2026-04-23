import unittest

from app.models.document import DocumentChunk
from app.rag.reranker import BGEReranker, KeywordReranker, build_reranker
from app.rag.vector_store import SearchMatch


class RerankerTests(unittest.TestCase):
    def test_prioritizes_matching_technology_stack_terms(self) -> None:
        matches = [
            SearchMatch(
                chunk=DocumentChunk(
                    doc_id="1",
                    chunk_id="1",
                    title="Redis timeout",
                    section_path=["Redis", "Timeout"],
                    content="Redis timeout should inspect memory and slowlog.",
                    source="redis.md",
                    order=0,
                    token_count=8,
                ),
                score=3.0,
            ),
            SearchMatch(
                chunk=DocumentChunk(
                    doc_id="2",
                    chunk_id="2",
                    title="MySQL slow query",
                    section_path=["MySQL", "Slow Query"],
                    content="MySQL slow query should inspect slow query log and explain.",
                    source="mysql.md",
                    order=1,
                    token_count=9,
                ),
                score=3.0,
            ),
        ]

        ranked = KeywordReranker().rerank("MySQL 慢查询需要看什么日志？", matches, limit=2)

        self.assertEqual(ranked[0].chunk.source, "mysql.md")

    def test_bge_reranker_uses_pair_scores_to_promote_best_match(self) -> None:
        matches = [
            SearchMatch(
                chunk=DocumentChunk(
                    doc_id="1",
                    chunk_id="1",
                    title="Redis timeout",
                    section_path=["Redis", "Timeout"],
                    content="Redis timeout should inspect memory and slowlog.",
                    source="redis.md",
                    order=0,
                    token_count=8,
                ),
                score=2.0,
            ),
            SearchMatch(
                chunk=DocumentChunk(
                    doc_id="2",
                    chunk_id="2",
                    title="MySQL slow query",
                    section_path=["MySQL", "Slow Query"],
                    content="MySQL slow query should inspect slow query log and explain.",
                    source="mysql.md",
                    order=1,
                    token_count=9,
                ),
                score=1.0,
            ),
        ]

        reranker = BGEReranker(model_name="BAAI/bge-reranker-v2-m3", scorer=lambda pairs: [0.2, 0.9])
        ranked = reranker.rerank("MySQL 慢查询需要看什么日志？", matches, limit=2)

        self.assertEqual(ranked[0].chunk.source, "mysql.md")
        self.assertEqual(reranker.backend_name(), "bge")

    def test_build_reranker_falls_back_to_keyword_when_bge_is_unavailable(self) -> None:
        class Settings:
            reranker_backend = "bge"
            bge_reranker_model = "BAAI/bge-reranker-v2-m3"

        reranker = build_reranker(Settings(), scorer=None, force_fallback=True)

        self.assertEqual(reranker.__class__.__name__, "KeywordReranker")


if __name__ == "__main__":
    unittest.main()
