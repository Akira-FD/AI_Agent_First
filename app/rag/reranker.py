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


class KeywordReranker:
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
