from __future__ import annotations

from app.rag.vector_store import SearchMatch


STACK_KEYWORDS = {
    "redis": {"redis", "redis-cli", "slowlog", "maxmemory"},
    "mysql": {"mysql", "slow query", "slow_query", "explain", "innodb"},
    "kubernetes": {"kubernetes", "k8s", "pod", "kubectl", "kubelet", "container runtime"},
    "nginx": {"nginx", "ingress"},
    "elasticsearch": {"elasticsearch", "es", "shard"},
    "prometheus": {"prometheus", "alertmanager", "promql"},
}


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
    def __init__(self, model_name: str, scorer=None) -> None:
        self.model_name = model_name
        self.scorer = scorer or self._build_default_scorer(model_name)

    def backend_name(self) -> str:
        return "bge"

    def rerank(self, query: str, matches: list[SearchMatch], limit: int) -> list[SearchMatch]:
        if not matches:
            return []
        pairs = [
            [
                query,
                "\n".join(
                    [
                        match.chunk.title,
                        " / ".join(match.chunk.section_path),
                        match.chunk.content,
                    ]
                ),
            ]
            for match in matches
        ]
        pair_scores = self.scorer(pairs)
        ranked = sorted(
            zip(matches, pair_scores, strict=False),
            key=lambda item: (float(item[1]), item[0].score),
            reverse=True,
        )
        return [match for match, _ in ranked[:limit]]

    def _build_default_scorer(self, model_name: str):
        from FlagEmbedding import FlagReranker  # type: ignore

        reranker = FlagReranker(model_name, use_fp16=False)
        return lambda pairs: reranker.compute_score(pairs)


def build_reranker(settings, scorer=None, force_fallback: bool = False) -> BaseReranker:
    backend = getattr(settings, "reranker_backend", "keyword").lower()
    if backend not in {"bge", "bge-reranker"}:
        return KeywordReranker()
    if force_fallback:
        return KeywordReranker()
    try:
        return BGEReranker(model_name=getattr(settings, "bge_reranker_model", "BAAI/bge-reranker-v2-m3"), scorer=scorer)
    except Exception:
        return KeywordReranker()
