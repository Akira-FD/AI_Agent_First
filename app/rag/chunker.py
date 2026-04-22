from __future__ import annotations

from app.models.document import DocumentChunk
from app.rag.markdown_parser import MarkdownSection


class MarkdownChunker:
    def __init__(self, target_words: int = 80) -> None:
        self.target_words = target_words

    def chunk_sections(self, doc_id: str, source: str, sections: list[MarkdownSection]) -> list[DocumentChunk]:
        chunks: list[DocumentChunk] = []
        chunk_order = 0
        for section in sections:
            text = section.text
            if not text:
                continue
            words = text.split()
            for start in range(0, len(words), self.target_words):
                part_words = words[start : start + self.target_words]
                content = " ".join(part_words)
                chunks.append(
                    DocumentChunk(
                        doc_id=doc_id,
                        chunk_id=f"{doc_id}-{chunk_order}",
                        title=section.title,
                        section_path=section.path,
                        content=content,
                        source=source,
                        order=chunk_order,
                        token_count=len(part_words),
                    )
                )
                chunk_order += 1
        return chunks
