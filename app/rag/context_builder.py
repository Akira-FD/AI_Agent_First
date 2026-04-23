from __future__ import annotations

from dataclasses import dataclass

from app.rag.vector_store import SearchMatch


@dataclass
class RetrievalResult:
    context_text: str
    sources: list[dict[str, str | float]]


class ContextBuilder:
    def __init__(self, max_context_chars: int = 2400, excerpt_chars: int = 120) -> None:
        self.max_context_chars = max_context_chars
        self.excerpt_chars = excerpt_chars

    def build(self, matches: list[SearchMatch]) -> RetrievalResult:
        context_parts: list[str] = []
        sources: list[dict[str, str | float]] = []
        used_chars = 0
        for match in matches:
            path = " > ".join(match.chunk.section_path)
            context_part = f"[{path}] {match.chunk.content}"
            remaining = self.max_context_chars - used_chars
            if remaining <= 0:
                break
            if len(context_part) > remaining:
                context_part = context_part[:remaining].rstrip()
            context_parts.append(context_part)
            used_chars += len(context_part) + 1
            sources.append(
                {
                    "title": match.chunk.title,
                    "source": match.chunk.source,
                    "section_path": path,
                    "chunk_id": match.chunk.chunk_id,
                    "score": round(match.score, 4),
                    "excerpt": match.chunk.content[: self.excerpt_chars],
                }
            )
        return RetrievalResult(context_text="\n".join(context_parts), sources=sources)
