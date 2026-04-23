from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.evaluation.report import write_eval_report
from app.evaluation.models import EvalCase
from app.evaluation.runner import EvaluationRunner
from app.main import bootstrap_application
from app.rag.ingest_pipeline import IngestPipeline


def load_cases(path: Path) -> list[EvalCase]:
    raw_cases = json.loads(path.read_text(encoding="utf-8"))
    return [
        EvalCase(
            id=item["id"],
            query=item["query"],
            expected_source=item["expected_source"],
            answer_keywords=item.get("answer_keywords", []),
            provenance_url=item.get("provenance_url", ""),
        )
        for item in raw_cases
    ]


def main() -> None:
    app = bootstrap_application(ROOT)
    IngestPipeline(settings=app.settings, repository=app.repository).ingest_directory(app.settings.docs_dir)
    cases = load_cases(ROOT / "evaluation" / "cases" / "github_cases.json")
    results = EvaluationRunner(agent=app.agent).run_cases(cases)
    paths = write_eval_report(results, ROOT / "evaluation" / "reports")
    print(f"Wrote JSON report to {paths['json']}")
    print(f"Wrote Markdown report to {paths['markdown']}")


if __name__ == "__main__":
    main()
