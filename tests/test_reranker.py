import unittest

from app.models.document import DocumentChunk
from app.rag.reranker import KeywordReranker
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


if __name__ == "__main__":
    unittest.main()
