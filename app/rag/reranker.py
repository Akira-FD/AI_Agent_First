from __future__ import annotations

from app.rag.vector_store import SearchMatch


class KeywordReranker:
    def rerank(self, query: str, matches: list[SearchMatch], limit: int) -> list[SearchMatch]:
        prioritized = sorted(
            matches,
            key=lambda item: (
                query.lower() in item.chunk.content.lower(),
                item.score,
            ),
            reverse=True,
        )
        return prioritized[:limit]
