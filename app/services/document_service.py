from __future__ import annotations


class DocumentService:
    def __init__(self, repository) -> None:
        self.repository = repository

    def list_documents(self):
        return self.repository.list_documents()
