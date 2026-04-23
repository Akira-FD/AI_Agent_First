from __future__ import annotations

from dataclasses import asdict, dataclass


@dataclass(frozen=True)
class EvalCase:
    id: str
    query: str
    expected_source: str
    answer_keywords: list[str]
    provenance_url: str


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

    def to_dict(self) -> dict[str, object]:
        return asdict(self)
