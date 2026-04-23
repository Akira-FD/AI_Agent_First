from __future__ import annotations

import json
from pathlib import Path

from app.evaluation.metrics import summarize_results
from app.evaluation.models import EvalResult


def write_eval_report(results: list[EvalResult], output_dir: Path) -> dict[str, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    summary = summarize_results(results)
    payload = {
        "summary": summary,
        "results": [result.to_dict() for result in results],
    }
    json_path = output_dir / "eval_report.json"
    markdown_path = output_dir / "eval_report.md"
    json_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    markdown_path.write_text(_to_markdown(summary, results), encoding="utf-8")
    return {"json": json_path, "markdown": markdown_path}


def _to_markdown(summary: dict[str, float | int], results: list[EvalResult]) -> str:
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
        "",
        "## Failed Cases",
        "",
    ]
    failed = [result for result in results if not result.passed]
    if not failed:
        lines.append("- None")
    else:
        for result in failed:
            lines.append(f"- `{result.id}` expected `{result.expected_source}`, got `{result.top_source}`")
    lines.append("")
    return "\n".join(lines)
