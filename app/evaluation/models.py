from __future__ import annotations

from dataclasses import asdict, dataclass, field


@dataclass(frozen=True)
class EvalCase:
    id: str
    query: str
    expected_source: str
    answer_keywords: list[str]
    provenance_url: str
    expected_plan_route: str = ""
    expected_plan_steps: list[str] = field(default_factory=list)
    expected_tool_names: list[str] = field(default_factory=list)
    expected_recovery_action: str = ""
    expected_replan_steps: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class EvalResult:
    id: str
    query: str
    expected_source: str
    top_source: str | None
    source_names: list[str]
    answer_preview: str
    checks: dict[str, bool]
    keyword_hit_count: int
    keyword_total: int
    passed: bool
    retrieval_backend: str = "unknown"
    embedding_backend: str = "unknown"
    vector_store_backend: str = "unknown"
    reranker_backend: str = "unknown"
    retrieval_stage_latency_ms: dict[str, int] = field(default_factory=dict)
    plan_route: str = ""
    plan_steps: list[str] = field(default_factory=list)
    node_trace: list[str] = field(default_factory=list)
    selected_tool: str = ""
    tool_actions: list[dict[str, object]] = field(default_factory=list)
    recovery_action: str = ""
    replan_steps: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, object]:
        return asdict(self)
