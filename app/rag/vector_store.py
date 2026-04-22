from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from app.models.document import DocumentChunk
from app.rag.embedding_service import SimpleEmbeddingService


@dataclass
class SearchMatch:
    chunk: DocumentChunk
    score: float


class InMemoryVectorStore:
    def __init__(self, embedding_service: SimpleEmbeddingService | None = None) -> None:
        self.embedding_service = embedding_service or SimpleEmbeddingService()

    def search(self, query: str, chunks: Iterable[DocumentChunk], top_k: int) -> list[SearchMatch]:
        query_tokens = self.embedding_service.embed(query)
        scored: list[SearchMatch] = []
        for chunk in chunks:
            chunk_tokens = self.embedding_service.embed(chunk.content + " " + " ".join(chunk.section_path))
            overlap = sum((query_tokens & chunk_tokens).values())
            if overlap > 0:
                scored.append(SearchMatch(chunk=chunk, score=float(overlap)))
        scored.sort(key=lambda item: item.score, reverse=True)
        return scored[:top_k]
