from __future__ import annotations

import time

from app.rag.context_builder import ContextBuilder, RetrievalResult
from app.rag.embedding_service import EmbeddingProvider, HashEmbeddingProvider
from app.rag.reranker import BaseReranker, KeywordReranker
from app.rag.vector_store import InMemoryVectorStore, VectorStore
from app.repositories.sqlite_repo import SQLiteRepository


class Retriever:
    def __init__(
        self,
        repository: SQLiteRepository,
        top_k: int = 5,
        max_context_chars: int = 2400,
        prefilter_limit: int = 6,
        vector_store: VectorStore | None = None,
        embedding_provider: EmbeddingProvider | None = None,
        reranker: BaseReranker | None = None,
        context_builder: ContextBuilder | None = None,
    ) -> None:
        self.repository = repository
        self.top_k = top_k
        self.prefilter_limit = max(top_k, prefilter_limit)
        self.embedding_provider = embedding_provider or HashEmbeddingProvider()
        self.vector_store = vector_store or InMemoryVectorStore(embedding_provider=self.embedding_provider)
        self.reranker = reranker or KeywordReranker()
        self.context_builder = context_builder or ContextBuilder(max_context_chars=max_context_chars)
        self._prefilter_reranker = KeywordReranker()

    def retrieve(self, query: str) -> RetrievalResult:
        chunks = self.repository.list_chunks()
        stage_started_at = time.monotonic()
        recalled = self.vector_store.search(query, chunks, top_k=max(self.top_k * 2, 4))
        retrieval_latency_ms = _elapsed_ms(stage_started_at)

        coarse_rerank_latency_ms = 0
        bge_rerank_latency_ms = 0
        if self.reranker.backend_name() == "bge":
            stage_started_at = time.monotonic()
            rerank_candidates = self._select_rerank_candidates(query, recalled)
            coarse_rerank_latency_ms = _elapsed_ms(stage_started_at)

            stage_started_at = time.monotonic()
            reranked = self.reranker.rerank(query, rerank_candidates, limit=self.top_k)
            bge_rerank_latency_ms = _elapsed_ms(stage_started_at)
        else:
            stage_started_at = time.monotonic()
            reranked = self.reranker.rerank(query, recalled, limit=self.top_k)
            coarse_rerank_latency_ms = _elapsed_ms(stage_started_at)

        stage_started_at = time.monotonic()
        result = self.context_builder.build(reranked)
        context_build_latency_ms = _elapsed_ms(stage_started_at)
        result.stage_latency_ms = {
            "retrieval": retrieval_latency_ms,
            "coarse_rerank": coarse_rerank_latency_ms,
            "bge_rerank": bge_rerank_latency_ms,
            "context_build": context_build_latency_ms,
        }
        return result

    def _select_rerank_candidates(self, query: str, recalled: list) -> list:
        if len(recalled) <= self.top_k:
            return recalled
        if self.reranker.backend_name() != "bge":
            return recalled
        limited = self._prefilter_reranker.rerank(query, recalled, limit=min(len(recalled), self.prefilter_limit))
        if len(limited) < self.top_k:
            return recalled[: self.top_k]
        return limited


def _elapsed_ms(started_at: float) -> int:
    return max(0, int(round((time.monotonic() - started_at) * 1000)))
