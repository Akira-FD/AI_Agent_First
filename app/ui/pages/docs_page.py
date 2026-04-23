from __future__ import annotations


class DocsPage:
    def __init__(self, document_service=None) -> None:
        self.document_service = document_service
        self.documents: list[dict[str, object]] = []

    def refresh(self) -> list[dict[str, object]]:
        if self.document_service is None:
            return self.documents
        self.documents = [
            {
                "id": document.id,
                "title": document.title,
                "source": document.source,
                "path": document.path,
                "file_size": document.file_size,
                "chunk_count": document.chunk_count,
                "updated_at": document.updated_at,
            }
            for document in self.document_service.list_documents()
        ]
        return self.documents
