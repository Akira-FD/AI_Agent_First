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
    response_tool_names = [
        str(action.get("tool_name", ""))
        for action in list(getattr(response, "tool_actions", []))
    ]
    if case.expected_plan_route:
        checks["plan_route"] = getattr(response, "plan_route", "") == case.expected_plan_route
    if case.expected_plan_steps:
        checks["plan_steps"] = list(getattr(response, "plan_steps", [])) == case.expected_plan_steps
    if case.expected_tool_names:
        checks["tool_names"] = response_tool_names == case.expected_tool_names
    if (
        case.expected_plan_route
        or case.expected_plan_steps
        or case.expected_tool_names
        or case.expected_recovery_action
        or case.expected_replan_steps
    ):
        checks["replan_steps"] = list(getattr(response, "replan_steps", [])) == case.expected_replan_steps
    if case.expected_recovery_action or case.expected_recovery_action == "":
        if (
            case.expected_plan_route
            or case.expected_plan_steps
            or case.expected_tool_names
            or case.expected_recovery_action
            or case.expected_replan_steps
        ):
            checks["recovery_action"] = getattr(response, "recovery_action", "") == case.expected_recovery_action
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
        retrieval_backend=getattr(response, "retrieval_backend", "unknown"),
        embedding_backend=getattr(response, "embedding_backend", "unknown"),
        vector_store_backend=getattr(
            response,
            "vector_store_backend",
            getattr(response, "retrieval_backend", "unknown"),
        ),
        reranker_backend=getattr(response, "reranker_backend", "unknown"),
        retrieval_stage_latency_ms=dict(getattr(response, "retrieval_stage_latency_ms", {}) or {}),
        plan_route=getattr(response, "plan_route", ""),
        plan_steps=list(getattr(response, "plan_steps", [])),
        node_trace=list(getattr(response, "node_trace", [])),
        selected_tool=getattr(response, "selected_tool", ""),
        tool_actions=list(getattr(response, "tool_actions", [])),
        recovery_action=getattr(response, "recovery_action", ""),
        replan_steps=list(getattr(response, "replan_steps", [])),
    )
