from __future__ import annotations

from app.evaluation.models import EvalResult


def summarize_results(results: list[EvalResult]) -> dict[str, float | int]:
    case_count = len(results)
    if case_count == 0:
        return {
            "case_count": 0,
            "passed_count": 0,
            "pass_rate": 0.0,
            "source_hit_rate": 0.0,
            "top1_source_accuracy": 0.0,
            "keyword_hit_rate": 0.0,
        }

    passed_count = sum(1 for result in results if result.passed)
    source_hit_count = sum(1 for result in results if result.checks.get("source_hit"))
    top1_count = sum(1 for result in results if result.checks.get("top1_source"))
    keyword_case_hits = sum(1 for result in results if result.checks.get("keywords"))
    return {
        "case_count": case_count,
        "passed_count": passed_count,
        "pass_rate": passed_count / case_count,
        "source_hit_rate": source_hit_count / case_count,
        "top1_source_accuracy": top1_count / case_count,
        "keyword_hit_rate": keyword_case_hits / case_count,
    }
