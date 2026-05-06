import unittest
from unittest.mock import patch

from app.models.document import DocumentChunk
from app.rag import reranker as reranker_module
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

    def test_bge_reranker_truncates_passage_text_before_scoring(self) -> None:
        matches = [
            SearchMatch(
                chunk=DocumentChunk(
                    doc_id="1",
                    chunk_id="1",
                    title="Redis timeout",
                    section_path=["Redis", "Timeout"],
                    content="x" * 2000,
                    source="redis.md",
                    order=0,
                    token_count=8,
                ),
                score=2.0,
            )
        ]
        captured_pairs: list[list[str]] = []

        def capture_scores(pairs):
            captured_pairs.extend(pairs)
            return [0.8]

        reranker = BGEReranker(
            model_name="BAAI/bge-reranker-v2-m3",
            scorer=capture_scores,
            text_max_chars=120,
        )

        reranker.rerank("Redis timeout", matches, limit=1)

        self.assertEqual(len(captured_pairs), 1)
        self.assertLessEqual(len(captured_pairs[0][1]), 120)
        self.assertIn("Redis timeout", captured_pairs[0][1])

    def test_bge_reranker_caches_scores_for_repeated_query_and_passages(self) -> None:
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
            )
        ]
        scorer_calls: list[list[list[str]]] = []

        def scorer(pairs):
            scorer_calls.append(pairs)
            return [0.8 for _ in pairs]

        reranker = BGEReranker(
            model_name="BAAI/bge-reranker-v2-m3",
            scorer=scorer,
        )

        reranker.rerank("Redis timeout 怎么排查？", matches, limit=1)
        reranker.rerank("Redis timeout 怎么排查？", matches, limit=1)

        self.assertEqual(len(scorer_calls), 1)

    def test_cached_flag_reranker_reuses_same_model_instance_for_same_config(self) -> None:
        class FakeFlagReranker:
            def __init__(self, model_name_or_path: str, **kwargs) -> None:
                self.model_name_or_path = model_name_or_path
                self.kwargs = kwargs

            def compute_score(self, sentence_pairs, **kwargs):
                return [0.0 for _ in sentence_pairs]

        reranker_module._FLAG_RERANKER_CACHE.clear()
        try:
            with patch("app.rag.reranker.FlagReranker", FakeFlagReranker):
                first = reranker_module._get_cached_flag_reranker(
                    model_name_or_path="local-model",
                    use_fp16=False,
                    devices="cpu",
                    batch_size=4,
                    query_max_length=64,
                    max_length=256,
                )
                second = reranker_module._get_cached_flag_reranker(
                    model_name_or_path="local-model",
                    use_fp16=False,
                    devices="cpu",
                    batch_size=4,
                    query_max_length=64,
                    max_length=256,
                )
        finally:
            reranker_module._FLAG_RERANKER_CACHE.clear()

        self.assertIs(first, second)

    def test_build_reranker_falls_back_to_keyword_when_bge_is_unavailable(self) -> None:
        class Settings:
            reranker_backend = "bge"
            bge_reranker_model = "BAAI/bge-reranker-v2-m3"

        reranker = build_reranker(Settings(), scorer=None, force_fallback=True)

        self.assertEqual(reranker.__class__.__name__, "KeywordReranker")

    def test_build_reranker_applies_bge_latency_tuning_settings(self) -> None:
        class Settings:
            reranker_backend = "bge"
            bge_reranker_model = "local-model"
            bge_reranker_text_max_chars = 900
            bge_reranker_batch_size = 12
            bge_reranker_query_max_length = 48
            bge_reranker_max_length = 160
            bge_reranker_use_fp16 = False
            bge_reranker_devices = "cpu"

        reranker = build_reranker(Settings(), scorer=lambda pairs: [0.0 for _ in pairs])

        self.assertEqual(reranker.text_max_chars, 900)
        self.assertEqual(reranker.batch_size, 12)
        self.assertEqual(reranker.query_max_length, 48)
        self.assertEqual(reranker.max_length, 160)
        self.assertFalse(reranker.use_fp16)
        self.assertEqual(reranker.devices, "cpu")


if __name__ == "__main__":
    unittest.main()
