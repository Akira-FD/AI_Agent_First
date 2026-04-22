from __future__ import annotations

from dataclasses import dataclass

from app.rag.vector_store import SearchMatch


@dataclass
class RetrievalResult:
    context_text: str
    sources: list[dict[str, str]]


class ContextBuilder:
    def build(self, matches: list[SearchMatch]) -> RetrievalResult:
        context_parts: list[str] = []
        sources: list[dict[str, str]] = []
        for match in matches:
            path = " > ".join(match.chunk.section_path)
            context_parts.append(f"[{path}] {match.chunk.content}")
            sources.append(
                {
                    "title": match.chunk.title,
                    "source": match.chunk.source,
                    "section_path": path,
                    "chunk_id": match.chunk.chunk_id,
                }
            )
        return RetrievalResult(context_text="\n".join(context_parts), sources=sources)
