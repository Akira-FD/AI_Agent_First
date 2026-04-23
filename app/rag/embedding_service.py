from __future__ import annotations

from collections import Counter
import math
import re


class EmbeddingProvider:
    def backend_name(self) -> str:
        raise NotImplementedError

    def embed_sparse(self, text: str) -> Counter[str]:
        raise NotImplementedError

    def embed_dense(self, text: str) -> list[float]:
        raise NotImplementedError


class SimpleEmbeddingService:
    def embed(self, text: str) -> Counter[str]:
        normalized = text.lower()
        latin_tokens = [
            token
            for token in re.findall(r"[a-z0-9_]+", normalized)
            if token
        ]
        cjk_chars = [char for char in normalized if "\u4e00" <= char <= "\u9fff"]
        cjk_bigrams = [normalized[index : index + 2] for index in range(len(normalized) - 1) if self._is_cjk_bigram(normalized[index : index + 2])]
        return Counter(latin_tokens + cjk_chars + cjk_bigrams)

    def _is_cjk_bigram(self, token: str) -> bool:
        return len(token) == 2 and all("\u4e00" <= char <= "\u9fff" for char in token)


class HashEmbeddingService:
    def __init__(self, dimension: int = 96) -> None:
        self.dimension = max(8, dimension)

    def embed_dense(self, text: str) -> list[float]:
        sparse = SimpleEmbeddingService().embed(text)
        vector = [0.0] * self.dimension
        for token, weight in sparse.items():
            index = hash(token) % self.dimension
            sign = -1.0 if hash(f"sign:{token}") % 2 else 1.0
            vector[index] += float(weight) * sign

        norm = math.sqrt(sum(value * value for value in vector))
        if norm == 0:
            return vector
        return [value / norm for value in vector]


class SparseTokenEmbeddingProvider(EmbeddingProvider):
    def __init__(self, service: SimpleEmbeddingService | None = None, dimension: int = 96) -> None:
        self.service = service or SimpleEmbeddingService()
        self.dimension = dimension

    def embed_sparse(self, text: str) -> Counter[str]:
        return self.service.embed(text)

    def embed_dense(self, text: str) -> list[float]:
        return HashEmbeddingService(dimension=self.dimension).embed_dense(text)

    def backend_name(self) -> str:
        return "sparse"


class HashEmbeddingProvider(EmbeddingProvider):
    def __init__(self, service: HashEmbeddingService | None = None, dimension: int = 96) -> None:
        self.service = service or HashEmbeddingService(dimension=dimension)

    def embed_sparse(self, text: str) -> Counter[str]:
        return SimpleEmbeddingService().embed(text)

    def embed_dense(self, text: str) -> list[float]:
        return self.service.embed_dense(text)

    def backend_name(self) -> str:
        return "hash"


def build_embedding_provider(settings) -> EmbeddingProvider:
    backend = getattr(settings, "embedding_backend", "hash").lower()
    dimension = getattr(settings, "milvus_dimension", 96)
    if backend == "sparse":
        return SparseTokenEmbeddingProvider(dimension=dimension)
    return HashEmbeddingProvider(dimension=dimension)
