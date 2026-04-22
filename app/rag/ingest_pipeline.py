from __future__ import annotations

from dataclasses import dataclass
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


class IngestPipeline:
    def __init__(
        self,
        settings,
        repository: SQLiteRepository,
        parser: MarkdownParser | None = None,
        chunker: MarkdownChunker | None = None,
    ) -> None:
        self.settings = settings
        self.repository = repository
        self.parser = parser or MarkdownParser()
        self.chunker = chunker or MarkdownChunker()

    def ingest_directory(self, docs_dir: Path) -> IngestResult:
        document_count = 0
        chunk_count = 0
        for path in sorted(docs_dir.rglob("*.md")):
            text = path.read_text(encoding="utf-8")
            sections = self.parser.parse(text)
            doc_id = uuid.uuid5(uuid.NAMESPACE_URL, str(path.resolve())).hex
            self.repository.delete_documents_by_path(str(path))
            document = DocumentRecord(
                id=doc_id,
                title=sections[0].title if sections else path.stem,
                source=path.name,
                path=str(path),
            )
            self.repository.upsert_document(document)
            chunks = self.chunker.chunk_sections(doc_id=doc_id, source=path.name, sections=sections)
            self.repository.replace_document_chunks(doc_id, chunks)
            document_count += 1
            chunk_count += len(chunks)
        return IngestResult(document_count=document_count, chunk_count=chunk_count)
