from __future__ import annotations

from app.rag.embedding_service import build_embedding_provider
from app.rag.reranker import build_reranker
from app.rag.retriever import Retriever
from app.rag.vector_store import build_vector_store


def build_retriever(settings, repository, client=None, requester=None, reranker_scorer=None) -> Retriever:
    embedding_provider = build_embedding_provider(settings)
    reranker = build_reranker(settings, scorer=reranker_scorer)
    vector_store = build_vector_store(
        settings,
        client=client,
        embedding_provider=embedding_provider,
        requester=requester,
    )
    return Retriever(
        repository=repository,
        top_k=settings.retrieval_top_k,
        vector_store=vector_store,
        embedding_provider=embedding_provider,
        reranker=reranker,
    )
