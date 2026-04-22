from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class DocumentRecord:
    id: str
    title: str
    source: str
    path: str


@dataclass
class DocumentChunk:
    doc_id: str
    chunk_id: str
    title: str
    section_path: list[str]
    content: str
    source: str
    order: int
    token_count: int
    tags: list[str] = field(default_factory=list)
