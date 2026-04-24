from __future__ import annotations

import json
from pathlib import Path

from app.evaluation.metrics import summarize_results, summarize_results_by_agent_path, summarize_results_by_backend
from app.evaluation.models import EvalResult


def write_eval_report(results: list[EvalResult], output_dir: Path) -> dict[str, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    summary = summarize_results(results)
    backend_comparison = summarize_results_by_backend(results)
    agent_path_comparison = summarize_results_by_agent_path(results)
    payload = {
        "summary": summary,
        "backend_comparison": backend_comparison,
        "agent_path_comparison": agent_path_comparison,
        "results": [result.to_dict() for result in results],
    }
    json_path = output_dir / "eval_report.json"
    markdown_path = output_dir / "eval_report.md"
    json_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    markdown_path.write_text(_to_markdown(summary, results), encoding="utf-8")
    return {"json": json_path, "markdown": markdown_path}


def _to_markdown(summary: dict[str, float | int], results: list[EvalResult]) -> str:
    backend_comparison = summarize_results_by_backend(results)
    agent_path_comparison = summarize_results_by_agent_path(results)
    lines = [
        "# Evaluation Report",
        "",
        "## Summary",
        "",
        f"- Case count: {summary['case_count']}",
        f"- Passed: {summary['passed_count']}",
        f"- Pass rate: {summary['pass_rate']:.2%}",
        f"- Source hit rate: {summary['source_hit_rate']:.2%}",
        f"- Top1 source accuracy: {summary['top1_source_accuracy']:.2%}",
        f"- Keyword hit rate: {summary['keyword_hit_rate']:.2%}",
        f"- Agent task success rate: {summary['agent_task_success_rate']:.2%}",
        "",
        "## Backend Comparison",
        "",
    ]
    if not backend_comparison:
        lines.append("- None")
    else:
        for item in backend_comparison:
            lines.append(
                "- "
                f"Retrieval=`{item['retrieval_backend']}`, "
                f"Embedding=`{item['embedding_backend']}`, "
                f"Vector store=`{item['vector_store_backend']}`, "
                f"Reranker=`{item['reranker_backend']}`; "
                f"cases={item['case_count']}, "
                f"passed={item['passed_count']}, "
                f"pass_rate={item['pass_rate']:.2%}, "
                f"top1={item['top1_source_accuracy']:.2%}, "
                f"keyword_hit={item['keyword_hit_rate']:.2%}"
            )
    lines.extend(
        [
            "",
            "## Agent Path Comparison",
            "",
        ]
    )
    if not agent_path_comparison:
        lines.append("- None")
    else:
        for item in agent_path_comparison:
            lines.append(
                "- "
                f"Plan=`{item['plan_route']}`, "
                f"Tool=`{item['selected_tool']}`, "
                f"Recovery=`{item['recovery_action']}`, "
                f"Replan=`{item['replan_steps']}`; "
                f"cases={item['case_count']}, "
                f"passed={item['passed_count']}, "
                f"pass_rate={item['pass_rate']:.2%}, "
                f"top1={item['top1_source_accuracy']:.2%}, "
                f"keyword_hit={item['keyword_hit_rate']:.2%}"
            )
    lines.extend(
        [
            "",
            "## Result Details",
            "",
        ]
    )
    if not results:
        lines.append("- None")
    else:
        for result in results:
            lines.append(f"- `{result.id}`")
            lines.append(f"  - Retrieval backend: `{result.retrieval_backend}`")
            lines.append(f"  - Embedding backend: `{result.embedding_backend}`")
            lines.append(f"  - Vector store backend: `{result.vector_store_backend}`")
            lines.append(f"  - Reranker backend: `{result.reranker_backend}`")
            if result.retrieval_stage_latency_ms:
                lines.append(
                    "  - Retrieval stage latency: `"
                    + _format_stage_latency(result.retrieval_stage_latency_ms)
                    + "`"
                )
            if result.plan_route:
                lines.append(f"  - Plan route: `{result.plan_route}`")
            if result.plan_steps:
                lines.append(f"  - Plan steps: `{' > '.join(result.plan_steps)}`")
            if result.node_trace:
                lines.append(f"  - Node trace: `{' > '.join(result.node_trace)}`")
            if result.selected_tool:
                lines.append(f"  - Selected tool: `{result.selected_tool}`")
            if result.tool_actions:
                tool_names = ", ".join(str(action.get("tool_name", "")) for action in result.tool_actions)
                lines.append(f"  - Tool actions: `{tool_names}`")
            if result.recovery_action:
                lines.append(f"  - Recovery action: `{result.recovery_action}`")
            if result.replan_steps:
                lines.append(f"  - Replan steps: `{' > '.join(result.replan_steps)}`")
    lines.extend(
        [
            "",
        "## Failed Cases",
        "",
        ]
    )
    failed = [result for result in results if not result.passed]
    if not failed:
        lines.append("- None")
    else:
        for result in failed:
            lines.append(f"- `{result.id}` expected `{result.expected_source}`, got `{result.top_source}`")
    lines.append("")
    return "\n".join(lines)


def _format_stage_latency(stage_latency_ms: dict[str, int]) -> str:
    ordered_keys = ["retrieval", "coarse_rerank", "bge_rerank", "context_build"]
    parts: list[str] = []
    for key in ordered_keys:
        if key in stage_latency_ms:
            parts.append(f"{key}={stage_latency_ms[key]}ms")
    for key, value in stage_latency_ms.items():
        if key not in ordered_keys:
            parts.append(f"{key}={value}ms")
    return ", ".join(parts)
