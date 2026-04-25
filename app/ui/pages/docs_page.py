from __future__ import annotations

from collections import Counter
from pathlib import Path


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

    def build_summary(self) -> dict[str, object]:
        documents = self.documents or self.refresh()
        total_chunks = 0
        category_counter: Counter[str] = Counter()
        key_topics: list[str] = []

        for document in documents:
            total_chunks += int(document.get("chunk_count", 0) or 0)
            topic = self._extract_topic(
                str(document.get("source", "")),
                str(document.get("title", "")),
            )
            category_counter[topic] += 1
            if topic not in key_topics:
                key_topics.append(topic)

        return {
            "document_count": len(documents),
            "chunk_count": total_chunks,
            "category_labels": [name for name, _count in category_counter.most_common(4)],
            "key_topics": key_topics[:6],
        }

    def _extract_topic(self, source: str, title: str) -> str:
        normalized = Path(source).stem.replace("_", " ").replace("-", " ").lower()
        mapping = {
            "redis": "Redis",
            "mysql": "MySQL",
            "kubernetes": "Kubernetes",
            "k8s": "Kubernetes",
            "milvus": "Milvus",
            "agent": "Agent",
            "rag": "RAG",
            "incident": "Incident",
        }
        for key, label in mapping.items():
            if key in normalized:
                return label

        if title.strip():
            return title.strip().split()[0]
        if normalized.strip():
            return normalized.title().split()[0]
        return "通用"
