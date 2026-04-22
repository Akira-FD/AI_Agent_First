from __future__ import annotations

from collections import Counter
import re


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
