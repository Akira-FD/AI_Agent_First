import json
import tempfile
import unittest
from pathlib import Path

from app.evaluation.graders import grade_response
from app.evaluation.metrics import summarize_results
from app.evaluation.models import EvalCase, EvalResult
from app.evaluation.report import write_eval_report
from app.evaluation.runner import EvaluationRunner


class StaticAgent:
    def run(self, session_id: str, user_query: str):
        return type(
            "Response",
            (),
            {
                "intent": "knowledge",
                "answer": "Check maxmemory and slowlog before restarting Redis.",
                "sources": [
                    {
                        "source": "redis-redis-issues-1.md",
                        "score": 4.2,
                        "section_path": "Redis > Answer",
                        "excerpt": "Check maxmemory and slowlog.",
                    }
                ],
                "tool_logs": [],
            },
        )()


class EvaluationRunnerTests(unittest.TestCase):
    def test_grades_response_against_expected_source_and_keywords(self) -> None:
        response = StaticAgent().run("s", "q")
        case = EvalCase(
            id="redis-1",
            query="How to handle Redis memory pressure?",
            expected_source="redis-redis-issues-1.md",
            answer_keywords=["maxmemory", "slowlog"],
            provenance_url="https://github.com/redis/redis/issues/1",
        )

        result = grade_response(case, response)

        self.assertTrue(result.passed)
        self.assertTrue(result.checks["source_hit"])
        self.assertTrue(result.checks["top1_source"])
        self.assertEqual(result.keyword_hit_count, 2)

    def test_runner_executes_cases_and_summarizes_metrics(self) -> None:
        cases = [
            EvalCase(
                id="redis-1",
                query="How to handle Redis memory pressure?",
                expected_source="redis-redis-issues-1.md",
                answer_keywords=["maxmemory", "slowlog"],
                provenance_url="https://github.com/redis/redis/issues/1",
            )
        ]

        results = EvaluationRunner(agent=StaticAgent()).run_cases(cases)
        summary = summarize_results(results)

        self.assertEqual(summary["case_count"], 1)
        self.assertEqual(summary["passed_count"], 1)
        self.assertEqual(summary["top1_source_accuracy"], 1.0)
        self.assertEqual(summary["keyword_hit_rate"], 1.0)

    def test_writes_json_and_markdown_report(self) -> None:
        result = EvalResult(
            id="redis-1",
            query="q",
            expected_source="redis-redis-issues-1.md",
            top_source="redis-redis-issues-1.md",
            source_names=["redis-redis-issues-1.md"],
            answer_preview="answer",
            checks={"source_hit": True, "top1_source": True, "keywords": True},
            keyword_hit_count=1,
            keyword_total=1,
            passed=True,
        )
        with tempfile.TemporaryDirectory() as tmpdir:
            output_dir = Path(tmpdir)

            paths = write_eval_report([result], output_dir)

            self.assertTrue(paths["json"].exists())
            self.assertTrue(paths["markdown"].exists())
            self.assertEqual(json.loads(paths["json"].read_text(encoding="utf-8"))["summary"]["passed_count"], 1)


if __name__ == "__main__":
    unittest.main()
