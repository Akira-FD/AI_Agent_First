from __future__ import annotations

from app.rag.vector_store import SearchMatch

try:
    from FlagEmbedding import FlagReranker as FlagReranker  # type: ignore
except Exception:  # pragma: no cover - optional dependency remains lazy/fallback-safe
    FlagReranker = None  # type: ignore


STACK_KEYWORDS = {
    "redis": {"redis", "redis-cli", "slowlog", "maxmemory"},
    "mysql": {"mysql", "slow query", "slow_query", "explain", "innodb"},
    "kubernetes": {"kubernetes", "k8s", "pod", "kubectl", "kubelet", "container runtime"},
    "nginx": {"nginx", "ingress"},
    "elasticsearch": {"elasticsearch", "es", "shard"},
    "prometheus": {"prometheus", "alertmanager", "promql"},
}

_FLAG_RERANKER_CACHE: dict[tuple[object, ...], object] = {}


class BaseReranker:
    def backend_name(self) -> str:
        raise NotImplementedError

    def rerank(self, query: str, matches: list[SearchMatch], limit: int) -> list[SearchMatch]:
        raise NotImplementedError


class KeywordReranker(BaseReranker):
    def backend_name(self) -> str:
        return "keyword-tech-weighted"

    def rerank(self, query: str, matches: list[SearchMatch], limit: int) -> list[SearchMatch]:
        query_lower = query.lower()
        prioritized = sorted(
            matches,
            key=lambda item: (
                self._stack_overlap_score(query_lower, item.chunk.content.lower(), " ".join(item.chunk.section_path).lower()),
                query_lower in item.chunk.content.lower(),
                item.score,
            ),
            reverse=True,
        )
        return prioritized[:limit]

    def _stack_overlap_score(self, query_lower: str, content_lower: str, path_lower: str) -> int:
        score = 0
        for keywords in STACK_KEYWORDS.values():
            query_hits = sum(1 for keyword in keywords if keyword in query_lower)
            if query_hits == 0:
                continue
            content_hits = sum(1 for keyword in keywords if keyword in content_lower or keyword in path_lower)
            score = max(score, query_hits * 10 + content_hits * 3)
        return score


class BGEReranker(BaseReranker):
    def __init__(
        self,
        model_name: str,
        scorer=None,
        *,
        text_max_chars: int = 1200,
        batch_size: int = 16,
        query_max_length: int = 64,
        max_length: int = 256,
        use_fp16: bool | None = None,
        devices: str | None = None,
        score_cache_size: int = 256,
    ) -> None:
        self.model_name = model_name
        self.text_max_chars = max(32, text_max_chars)
        self.batch_size = batch_size
        self.query_max_length = query_max_length
        self.max_length = max_length
        self.use_fp16 = _should_use_fp16() if use_fp16 is None else use_fp16
        self.devices = devices or _default_reranker_device()
        self.score_cache_size = max(0, score_cache_size)
        self._pair_score_cache: dict[tuple[str, str], float] = {}
        self.scorer = scorer or self._build_default_scorer(model_name)

    def backend_name(self) -> str:
        return "bge"

    def rerank(self, query: str, matches: list[SearchMatch], limit: int) -> list[SearchMatch]:
        if not matches:
            return []
        passages = [self._build_passage_text(match) for match in matches]
        cache_keys = [(query, passage) for passage in passages]
        missing_pairs = [[query, passage] for cache_key, passage in zip(cache_keys, passages, strict=False) if cache_key not in self._pair_score_cache]
        if missing_pairs:
            missing_scores = self.scorer(missing_pairs)
            for pair, score in zip(missing_pairs, missing_scores, strict=False):
                self._remember_pair_score(pair[0], pair[1], float(score))
        pair_scores = [self._pair_score_cache.get(cache_key, 0.0) for cache_key in cache_keys]
        ranked = sorted(
            zip(matches, pair_scores, strict=False),
            key=lambda item: (float(item[1]), item[0].score),
            reverse=True,
        )
        return [match for match, _ in ranked[:limit]]

    def _build_passage_text(self, match: SearchMatch) -> str:
        passage = "\n".join(
            [
                match.chunk.title,
                " / ".join(match.chunk.section_path),
                match.chunk.content,
            ]
        )
        if len(passage) <= self.text_max_chars:
            return passage
        return passage[: self.text_max_chars].rstrip()

    def _build_default_scorer(self, model_name: str):
        reranker = _get_cached_flag_reranker(
            model_name_or_path=model_name,
            use_fp16=self.use_fp16,
            devices=self.devices,
            batch_size=self.batch_size,
            query_max_length=self.query_max_length,
            max_length=self.max_length,
        )
        return lambda pairs: reranker.compute_score(pairs)

    def _remember_pair_score(self, query: str, passage: str, score: float) -> None:
        if self.score_cache_size <= 0:
            return
        cache_key = (query, passage)
        self._pair_score_cache.pop(cache_key, None)
        self._pair_score_cache[cache_key] = score
        while len(self._pair_score_cache) > self.score_cache_size:
            oldest_key = next(iter(self._pair_score_cache))
            del self._pair_score_cache[oldest_key]


def build_reranker(settings, scorer=None, force_fallback: bool = False) -> BaseReranker:
    backend = getattr(settings, "reranker_backend", "keyword").lower()
    if backend not in {"bge", "bge-reranker"}:
        return KeywordReranker()
    if force_fallback:
        return KeywordReranker()
    try:
        return BGEReranker(
            model_name=getattr(settings, "bge_reranker_model", "BAAI/bge-reranker-v2-m3"),
            scorer=scorer,
            text_max_chars=getattr(settings, "bge_reranker_text_max_chars", 900),
            batch_size=getattr(settings, "bge_reranker_batch_size", 12),
            query_max_length=getattr(settings, "bge_reranker_query_max_length", 48),
            max_length=getattr(settings, "bge_reranker_max_length", 160),
            use_fp16=getattr(settings, "bge_reranker_use_fp16", None),
            devices=getattr(settings, "bge_reranker_devices", "") or None,
            score_cache_size=getattr(settings, "bge_reranker_score_cache_size", 256),
        )
    except Exception:
        return KeywordReranker()


def _get_cached_flag_reranker(
    *,
    model_name_or_path: str,
    use_fp16: bool,
    devices: str | None,
    batch_size: int,
    query_max_length: int,
    max_length: int,
):
    key = (
        model_name_or_path,
        use_fp16,
        devices,
        batch_size,
        query_max_length,
        max_length,
    )
    cached = _FLAG_RERANKER_CACHE.get(key)
    if cached is not None:
        return cached
    reranker_cls = FlagReranker
    if reranker_cls is None:
        raise ImportError("FlagEmbedding is not available")
    reranker = reranker_cls(
        model_name_or_path,
        use_fp16=use_fp16,
        devices=devices,
        batch_size=batch_size,
        query_max_length=query_max_length,
        max_length=max_length,
    )
    _FLAG_RERANKER_CACHE[key] = reranker
    return reranker


def _default_reranker_device() -> str:
    try:
        import torch

        if torch.cuda.is_available():
            return "cuda"
    except Exception:
        pass
    return "cpu"


def _should_use_fp16() -> bool:
    return _default_reranker_device() == "cuda"
