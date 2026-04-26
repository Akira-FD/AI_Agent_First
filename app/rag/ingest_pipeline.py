from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
import uuid

from app.models.document import DocumentRecord
from app.rag.chunker import MarkdownChunker
from app.rag.markdown_parser import MarkdownParser
from app.repositories.sqlite_repo import SQLiteRepository


@dataclass
class IngestResult:
    document_count: int
    chunk_count: int
    indexed_chunk_count: int = 0


class IngestPipeline:
    def __init__(
        self,
        settings,
        repository: SQLiteRepository,
        parser: MarkdownParser | None = None,
        chunker: MarkdownChunker | None = None,
        vector_indexer=None,
    ) -> None:
        self.settings = settings
        self.repository = repository
        self.parser = parser or MarkdownParser()
        self.chunker = chunker or MarkdownChunker()
        self.vector_indexer = vector_indexer

    def ingest_directory(self, docs_dir: Path) -> IngestResult:
        document_count = 0
        chunk_count = 0
        indexed_chunk_count = 0
        for path in sorted(docs_dir.rglob("*.md")):
            text = path.read_text(encoding="utf-8")
            sections = self.parser.parse(text)
            doc_id = uuid.uuid5(uuid.NAMESPACE_URL, str(path.resolve())).hex
            self.repository.delete_documents_by_path(str(path))
            chunks = self.chunker.chunk_sections(doc_id=doc_id, source=path.name, sections=sections)
            now = datetime.now(timezone.utc).isoformat()
            document = DocumentRecord(
                id=doc_id,
                title=sections[0].title if sections else path.stem,
                source=path.name,
                path=str(path),
                file_size=path.stat().st_size,
                chunk_count=len(chunks),
                created_at=now,
                updated_at=now,
            )
            self.repository.upsert_document(document)
            self.repository.replace_document_chunks(doc_id, chunks)
            if self.vector_indexer is not None:
                indexed_chunk_count += self.vector_indexer.upsert_chunks(chunks)
            document_count += 1
            chunk_count += len(chunks)
        if self.vector_indexer is not None and hasattr(self.vector_indexer, "finalize_ingest"):
            self.vector_indexer.finalize_ingest()
        return IngestResult(
            document_count=document_count,
            chunk_count=chunk_count,
            indexed_chunk_count=indexed_chunk_count,
        )
