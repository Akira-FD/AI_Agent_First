from __future__ import annotations

from app.evaluation.models import EvalCase, EvalResult


def grade_response(case: EvalCase, response) -> EvalResult:
    source_names = [source.get("source") for source in response.sources]
    top_source = source_names[0] if source_names else None
    answer_lower = response.answer.lower()
    keyword_hit_count = sum(1 for keyword in case.answer_keywords if keyword.lower() in answer_lower)
    checks = {
        "source_hit": case.expected_source in source_names,
        "top1_source": top_source == case.expected_source,
        "keywords": keyword_hit_count > 0 if case.answer_keywords else True,
    }
    return EvalResult(
        id=case.id,
        query=case.query,
        expected_source=case.expected_source,
        top_source=top_source,
        source_names=source_names,
        answer_preview=response.answer[:240].replace("\n", " "),
        checks=checks,
        keyword_hit_count=keyword_hit_count,
        keyword_total=len(case.answer_keywords),
        passed=all(checks.values()),
    )
