from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable
import json
import urllib.request

from app.models.document import DocumentChunk
from app.rag.embedding_service import EmbeddingProvider, HashEmbeddingProvider, SimpleEmbeddingService


@dataclass
class SearchMatch:
    chunk: DocumentChunk
    score: float


class VectorStore:
    def backend_name(self) -> str:
        raise NotImplementedError

    def upsert_chunks(self, chunks: Iterable[DocumentChunk]) -> int:
        raise NotImplementedError

    def search(self, query: str, chunks: Iterable[DocumentChunk], top_k: int) -> list[SearchMatch]:
        raise NotImplementedError


class InMemoryVectorStore(VectorStore):
    def __init__(self, embedding_provider: EmbeddingProvider | None = None) -> None:
        self.embedding_provider = embedding_provider or HashEmbeddingProvider()

    def upsert_chunks(self, chunks: Iterable[DocumentChunk]) -> int:
        return sum(1 for _ in chunks)

    def backend_name(self) -> str:
        return "in-memory"

    def search(self, query: str, chunks: Iterable[DocumentChunk], top_k: int) -> list[SearchMatch]:
        query_tokens = self.embedding_provider.embed_sparse(query)
        scored: list[SearchMatch] = []
        for chunk in chunks:
            chunk_tokens = self.embedding_provider.embed_sparse(chunk.content + " " + " ".join(chunk.section_path))
            overlap = sum((query_tokens & chunk_tokens).values())
            if overlap > 0:
                scored.append(SearchMatch(chunk=chunk, score=float(overlap)))
        scored.sort(key=lambda item: item.score, reverse=True)
        return scored[:top_k]


class MilvusVectorStore(VectorStore):
    def __init__(
        self,
        client,
        collection_name: str,
        embedding_provider: EmbeddingProvider | None = None,
        embedding_service=None,
        dimension: int = 96,
        backend_label: str = "milvus",
    ) -> None:
        self.client = client
        self.collection_name = collection_name
        self._backend_label = backend_label
        if embedding_provider is not None:
            self.embedding_provider = embedding_provider
        elif embedding_service is not None:
            self.embedding_provider = embedding_service
        else:
            self.embedding_provider = HashEmbeddingProvider(dimension=dimension)
        self.dimension = dimension
        self._ensure_collection()

    def _ensure_collection(self) -> None:
        if hasattr(self.client, "has_collection") and self.client.has_collection(collection_name=self.collection_name):
            return
        if hasattr(self.client, "create_collection"):
            self.client.create_collection(
                collection_name=self.collection_name,
                dimension=self.dimension,
                metric_type="COSINE",
            )

    def upsert_chunks(self, chunks: Iterable[DocumentChunk]) -> int:
        payload = []
        for chunk in chunks:
            payload.append(
                {
                    "chunk_id": chunk.chunk_id,
                    "doc_id": chunk.doc_id,
                    "title": chunk.title,
                    "source": chunk.source,
                    "section_path": " / ".join(chunk.section_path),
                    "content": chunk.content,
                    "vector": self.embedding_provider.embed_dense(
                        f"{chunk.title}\n{' '.join(chunk.section_path)}\n{chunk.content}"
                    ),
                }
            )
        if not payload:
            return 0
        self.client.upsert(collection_name=self.collection_name, data=payload)
        return len(payload)

    def search(self, query: str, chunks: Iterable[DocumentChunk], top_k: int) -> list[SearchMatch]:
        chunk_by_id = {chunk.chunk_id: chunk for chunk in chunks}
        results = self.client.search(
            collection_name=self.collection_name,
            data=[self.embedding_provider.embed_dense(query)],
            limit=top_k,
            output_fields=["chunk_id"],
            search_params={"metric_type": "COSINE"},
        )
        matches: list[SearchMatch] = []
        for item in results[0]:
            entity = item.get("entity", {})
            chunk_id = entity.get("chunk_id")
            chunk = chunk_by_id.get(chunk_id)
            if chunk is None:
                continue
            score = float(item.get("distance", 0.0))
            matches.append(SearchMatch(chunk=chunk, score=score))
        return matches

    def backend_name(self) -> str:
        return self._backend_label


class RemoteVectorStore(VectorStore):
    def __init__(self, endpoint_url: str, requester=None) -> None:
        self.endpoint_url = endpoint_url
        self.requester = requester or self._default_requester

    def upsert_chunks(self, chunks: Iterable[DocumentChunk]) -> int:
        return 0

    def backend_name(self) -> str:
        return "remote"

    def search(self, query: str, chunks: Iterable[DocumentChunk], top_k: int) -> list[SearchMatch]:
        response = self.requester(self.endpoint_url, {"query": query, "top_k": top_k})
        chunk_by_id = {chunk.chunk_id: chunk for chunk in chunks}
        matches: list[SearchMatch] = []
        for item in response.get("matches", []):
            chunk = chunk_by_id.get(item.get("chunk_id"))
            if chunk is None:
                continue
            matches.append(SearchMatch(chunk=chunk, score=float(item.get("score", 0.0))))
        return matches

    def _default_requester(self, endpoint_url: str, payload: dict[str, object]) -> dict[str, object]:
        request = urllib.request.Request(
            endpoint_url,
            data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(request, timeout=15) as response:
            return json.loads(response.read().decode("utf-8"))


def _create_milvus_client(uri: str):
    from pymilvus import MilvusClient  # type: ignore

    return MilvusClient(uri=uri)


def build_vector_store(settings, client=None, embedding_provider: EmbeddingProvider | None = None, requester=None) -> VectorStore:
    backend = getattr(settings, "retrieval_backend", "in-memory").lower()
    if backend == "remote":
        return RemoteVectorStore(
            endpoint_url=getattr(settings, "remote_retrieval_url", ""),
            requester=requester,
        )
    if backend == "milvus-lite":
        try:
            milvus_client = client or _create_milvus_client(str(getattr(settings, "milvus_lite_path")))
            return MilvusVectorStore(
                client=milvus_client,
                collection_name=getattr(settings, "milvus_collection", "ai_agent_first_chunks"),
                embedding_provider=embedding_provider,
                dimension=getattr(settings, "milvus_dimension", 96),
                backend_label="milvus-lite",
            )
        except Exception:
            return InMemoryVectorStore(embedding_provider=embedding_provider)
    if backend != "milvus" or not getattr(settings, "milvus_enabled", False):
        return InMemoryVectorStore(embedding_provider=embedding_provider)
    try:
        milvus_client = client or _create_milvus_client(getattr(settings, "milvus_uri", "http://localhost:19530"))
        return MilvusVectorStore(
            client=milvus_client,
            collection_name=getattr(settings, "milvus_collection", "ai_agent_first_chunks"),
            embedding_provider=embedding_provider,
            dimension=getattr(settings, "milvus_dimension", 96),
            backend_label="milvus",
        )
    except Exception:
        return InMemoryVectorStore(embedding_provider=embedding_provider)
