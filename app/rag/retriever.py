from __future__ import annotations

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
        vector_store: VectorStore | None = None,
        embedding_provider: EmbeddingProvider | None = None,
        reranker: BaseReranker | None = None,
        context_builder: ContextBuilder | None = None,
    ) -> None:
        self.repository = repository
        self.top_k = top_k
        self.embedding_provider = embedding_provider or HashEmbeddingProvider()
        self.vector_store = vector_store or InMemoryVectorStore(embedding_provider=self.embedding_provider)
        self.reranker = reranker or KeywordReranker()
        self.context_builder = context_builder or ContextBuilder(max_context_chars=max_context_chars)

    def retrieve(self, query: str) -> RetrievalResult:
        chunks = self.repository.list_chunks()
        recalled = self.vector_store.search(query, chunks, top_k=max(self.top_k * 2, 4))
        reranked = self.reranker.rerank(query, recalled, limit=self.top_k)
        return self.context_builder.build(reranked)
