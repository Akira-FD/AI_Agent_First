from __future__ import annotations

from app.models.document import DocumentChunk
from app.rag.markdown_parser import MarkdownSection


class MarkdownChunker:
    fence_prefixes = ("```", "~~~")

    def __init__(self, target_words: int = 80, overlap_words: int = 12) -> None:
        self.target_words = target_words
        self.overlap_words = max(0, min(overlap_words, max(target_words - 1, 0)))

    def chunk_sections(self, doc_id: str, source: str, sections: list[MarkdownSection]) -> list[DocumentChunk]:
        chunks: list[DocumentChunk] = []
        chunk_order = 0
        for section in sections:
            blocks = self._split_text_blocks(section.text)
            if not blocks:
                continue
            for block in blocks:
                block_chunks = [block] if self._is_code_block(block) else self._split_plain_text(block)
                for content in block_chunks:
                    words = content.split()
                    token_count = len(words) if words else len(content)
                    if not content.strip():
                        continue
                    chunks.append(
                        DocumentChunk(
                            doc_id=doc_id,
                            chunk_id=f"{doc_id}-{chunk_order}",
                            title=section.title,
                            section_path=section.path,
                            content=content.strip(),
                            source=source,
                            order=chunk_order,
                            token_count=token_count,
                        )
                    )
                    chunk_order += 1
        return chunks

    def _split_text_blocks(self, text: str) -> list[str]:
        blocks: list[str] = []
        plain_lines: list[str] = []
        code_lines: list[str] = []
        in_code_fence = False

        for line in text.splitlines():
            if line.strip().startswith(self.fence_prefixes):
                if in_code_fence:
                    code_lines.append(line)
                    blocks.append("\n".join(code_lines))
                    code_lines = []
                    in_code_fence = False
                else:
                    if plain_lines:
                        blocks.append("\n".join(plain_lines).strip())
                        plain_lines = []
                    code_lines.append(line)
                    in_code_fence = True
                continue

            if in_code_fence:
                code_lines.append(line)
            else:
                plain_lines.append(line)

        if code_lines:
            blocks.append("\n".join(code_lines))
        if plain_lines:
            blocks.append("\n".join(plain_lines).strip())
        return [block for block in blocks if block.strip()]

    def _is_code_block(self, block: str) -> bool:
        return block.lstrip().startswith(self.fence_prefixes)

    def _split_plain_text(self, text: str) -> list[str]:
        words = text.split()
        if len(words) <= self.target_words:
            return [text]

        chunks: list[str] = []
        start = 0
        step = max(1, self.target_words - self.overlap_words)
        while start < len(words):
            part_words = words[start : start + self.target_words]
            chunks.append(" ".join(part_words))
            if start + self.target_words >= len(words):
                break
            start += step
        return chunks
