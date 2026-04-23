from __future__ import annotations

from collections import defaultdict

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
            "agent_task_success_rate": 0.0,
        }

    passed_count = sum(1 for result in results if result.passed)
    source_hit_count = sum(1 for result in results if result.checks.get("source_hit"))
    top1_count = sum(1 for result in results if result.checks.get("top1_source"))
    keyword_case_hits = sum(1 for result in results if result.checks.get("keywords"))
    agent_task_cases = [
        result
        for result in results
        if any(key in result.checks for key in ("plan_route", "plan_steps", "tool_names", "recovery_action", "replan_steps"))
    ]
    agent_task_hits = sum(
        1
        for result in agent_task_cases
        if all(result.checks.get(key, True) for key in ("plan_route", "plan_steps", "tool_names", "recovery_action", "replan_steps"))
    )
    return {
        "case_count": case_count,
        "passed_count": passed_count,
        "pass_rate": passed_count / case_count,
        "source_hit_rate": source_hit_count / case_count,
        "top1_source_accuracy": top1_count / case_count,
        "keyword_hit_rate": keyword_case_hits / case_count,
        "agent_task_success_rate": agent_task_hits / len(agent_task_cases) if agent_task_cases else 1.0,
    }


def summarize_results_by_backend(results: list[EvalResult]) -> list[dict[str, float | int | str]]:
    grouped: defaultdict[tuple[str, str, str, str], list[EvalResult]] = defaultdict(list)
    for result in results:
        key = (
            result.retrieval_backend,
            result.embedding_backend,
            result.vector_store_backend,
            result.reranker_backend,
        )
        grouped[key].append(result)

    summaries: list[dict[str, float | int | str]] = []
    for key, group in sorted(grouped.items()):
        summary = summarize_results(group)
        summaries.append(
            {
                "retrieval_backend": key[0],
                "embedding_backend": key[1],
                "vector_store_backend": key[2],
                "reranker_backend": key[3],
                **summary,
            }
        )
    return summaries


def summarize_results_by_agent_path(results: list[EvalResult]) -> list[dict[str, float | int | str]]:
    grouped: defaultdict[tuple[str, str, str, str], list[EvalResult]] = defaultdict(list)
    for result in results:
        key = (
            result.plan_route or "unknown",
            result.selected_tool or "none",
            result.recovery_action or "none",
            " > ".join(result.replan_steps) if result.replan_steps else "none",
        )
        grouped[key].append(result)

    summaries: list[dict[str, float | int | str]] = []
    for key, group in sorted(grouped.items()):
        summary = summarize_results(group)
        summaries.append(
            {
                "plan_route": key[0],
                "selected_tool": key[1],
                "recovery_action": key[2],
                "replan_steps": key[3],
                **summary,
            }
        )
    return summaries
