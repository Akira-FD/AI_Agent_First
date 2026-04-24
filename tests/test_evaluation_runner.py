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
                "retrieval_backend": "in-memory",
                "embedding_backend": "hash",
                "vector_store_backend": "in-memory",
                "reranker_backend": "keyword-tech-weighted",
                "plan_route": "tool",
                "plan_steps": ["retrieve_context", "restart_mock_service", "answer_with_tool_results"],
                "node_trace": [
                    "load_memory",
                    "persist_user_message",
                    "intent",
                    "retrieve",
                    "plan",
                    "tool_router",
                    "tool_exec",
                    "answer",
                    "persist_assistant_message",
                    "summary",
                ],
                "selected_tool": "restart_mock_service",
                "tool_actions": [
                    {"tool_name": "restart_mock_service", "tool_input": {"service_name": "redis"}},
                ],
                "recovery_action": "",
                "replan_steps": [],
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

    def test_grades_agent_path_against_expected_task_behavior(self) -> None:
        response = StaticAgent().run("s", "q")
        case = EvalCase(
            id="redis-tool-1",
            query="Restart Redis safely.",
            expected_source="redis-redis-issues-1.md",
            answer_keywords=["maxmemory"],
            provenance_url="https://github.com/redis/redis/issues/1",
            expected_plan_route="tool",
            expected_plan_steps=["retrieve_context", "restart_mock_service", "answer_with_tool_results"],
            expected_tool_names=["restart_mock_service"],
            expected_recovery_action="",
            expected_replan_steps=[],
        )

        result = grade_response(case, response)

        self.assertTrue(result.passed)
        self.assertTrue(result.checks["plan_route"])
        self.assertTrue(result.checks["plan_steps"])
        self.assertTrue(result.checks["tool_names"])
        self.assertTrue(result.checks["recovery_action"])
        self.assertTrue(result.checks["replan_steps"])

    def test_agent_path_mismatch_fails_case(self) -> None:
        response = StaticAgent().run("s", "q")
        case = EvalCase(
            id="redis-tool-2",
            query="Restart Redis safely.",
            expected_source="redis-redis-issues-1.md",
            answer_keywords=["maxmemory"],
            provenance_url="https://github.com/redis/redis/issues/1",
            expected_plan_route="answer",
            expected_plan_steps=["retrieve_context", "answer_with_context"],
            expected_tool_names=["check_service_status"],
            expected_recovery_action="degrade_to_answer",
            expected_replan_steps=["degrade_to_answer", "answer_with_available_context"],
        )

        result = grade_response(case, response)

        self.assertFalse(result.passed)
        self.assertFalse(result.checks["plan_route"])
        self.assertFalse(result.checks["plan_steps"])
        self.assertFalse(result.checks["tool_names"])
        self.assertFalse(result.checks["recovery_action"])
        self.assertFalse(result.checks["replan_steps"])

    def test_grades_fallback_to_remaining_actions_replan(self) -> None:
        response = type(
            "Response",
            (),
            {
                "answer": "已根据日志继续分析，发现 timeout 相关错误。",
                "sources": [{"source": "redis-redis-issues-1.md"}],
                "retrieval_backend": "in-memory",
                "embedding_backend": "hash",
                "vector_store_backend": "in-memory",
                "reranker_backend": "keyword-tech-weighted",
                "plan_route": "tool",
                "plan_steps": ["retrieve_context", "check_service_status", "search_error_logs", "answer_with_tool_results"],
                "node_trace": ["intent", "retrieve", "plan", "tool_router", "tool_exec", "observation", "recovery", "replan", "tool_exec", "answer"],
                "selected_tool": "check_service_status",
                "tool_actions": [
                    {"tool_name": "check_service_status", "tool_input": {"service_name": "redis"}},
                    {"tool_name": "search_error_logs", "tool_input": {"keyword": "timeout"}},
                ],
                "recovery_action": "fallback_to_remaining_actions",
                "replan_steps": ["fallback_to_remaining_actions", "search_error_logs", "answer_with_tool_results"],
            },
        )()
        case = EvalCase(
            id="redis-tool-fallback",
            query="请先查询 redis 状态，再查一下 timeout 相关日志",
            expected_source="redis-redis-issues-1.md",
            answer_keywords=["timeout"],
            provenance_url="https://github.com/redis/redis/issues/1",
            expected_plan_route="tool",
            expected_plan_steps=["retrieve_context", "check_service_status", "search_error_logs", "answer_with_tool_results"],
            expected_tool_names=["check_service_status", "search_error_logs"],
            expected_recovery_action="fallback_to_remaining_actions",
            expected_replan_steps=["fallback_to_remaining_actions", "search_error_logs", "answer_with_tool_results"],
        )

        result = grade_response(case, response)

        self.assertTrue(result.passed)
        self.assertTrue(result.checks["recovery_action"])
        self.assertTrue(result.checks["replan_steps"])

    def test_grades_status_logs_summary_tool_chain(self) -> None:
        response = type(
            "Response",
            (),
            {
                "answer": "已执行模拟工具。事件 INC-001 摘要已生成。",
                "sources": [{"source": "redis-redis-issues-1.md"}],
                "retrieval_backend": "in-memory",
                "embedding_backend": "hash",
                "vector_store_backend": "in-memory",
                "reranker_backend": "keyword-tech-weighted",
                "plan_route": "tool",
                "plan_steps": [
                    "retrieve_context",
                    "check_service_status",
                    "search_error_logs",
                    "get_incident_summary",
                    "answer_with_tool_results",
                ],
                "node_trace": ["intent", "retrieve", "plan", "tool_router", "tool_exec", "tool_exec", "tool_exec", "answer"],
                "selected_tool": "check_service_status",
                "tool_actions": [
                    {"tool_name": "check_service_status", "tool_input": {"service_name": "redis"}},
                    {"tool_name": "search_error_logs", "tool_input": {"keyword": "timeout"}},
                    {"tool_name": "get_incident_summary", "tool_input": {"service_name": "redis", "keyword": "timeout"}},
                ],
                "recovery_action": "",
                "replan_steps": [],
            },
        )()
        case = EvalCase(
            id="redis-tool-summary",
            query="请先查询 redis 状态，再查一下 timeout 相关日志，最后给我总结根因",
            expected_source="redis-redis-issues-1.md",
            answer_keywords=["摘要"],
            provenance_url="https://github.com/redis/redis/issues/1",
            expected_plan_route="tool",
            expected_plan_steps=[
                "retrieve_context",
                "check_service_status",
                "search_error_logs",
                "get_incident_summary",
                "answer_with_tool_results",
            ],
            expected_tool_names=["check_service_status", "search_error_logs", "get_incident_summary"],
            expected_recovery_action="",
            expected_replan_steps=[],
        )

        result = grade_response(case, response)

        self.assertTrue(result.passed)
        self.assertEqual(
            [action["tool_name"] for action in result.tool_actions],
            ["check_service_status", "search_error_logs", "get_incident_summary"],
        )

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
        self.assertEqual(summary["agent_task_success_rate"], 1.0)
        self.assertEqual(results[0].retrieval_backend, "in-memory")
        self.assertEqual(results[0].embedding_backend, "hash")
        self.assertEqual(results[0].vector_store_backend, "in-memory")
        self.assertEqual(results[0].reranker_backend, "keyword-tech-weighted")
        self.assertEqual(results[0].plan_route, "tool")
        self.assertEqual(
            results[0].plan_steps,
            ["retrieve_context", "restart_mock_service", "answer_with_tool_results"],
        )
        self.assertIn("tool_exec", results[0].node_trace)
        self.assertEqual(results[0].selected_tool, "restart_mock_service")
        self.assertEqual(results[0].tool_actions[0]["tool_name"], "restart_mock_service")

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
            retrieval_backend="remote",
            embedding_backend="hash",
            vector_store_backend="remote",
            reranker_backend="keyword-tech-weighted",
            plan_route="tool",
            plan_steps=["retrieve_context", "restart_mock_service", "answer_with_tool_results"],
            node_trace=["intent", "retrieve", "plan", "tool_router", "tool_exec", "answer"],
            selected_tool="restart_mock_service",
            tool_actions=[{"tool_name": "restart_mock_service", "tool_input": {"service_name": "redis"}}],
            recovery_action="retry_repaired_action",
            replan_steps=["retry_repaired_action", "restart_mock_service", "answer_with_tool_results"],
            retrieval_stage_latency_ms={
                "retrieval": 42,
                "coarse_rerank": 8,
                "bge_rerank": 31,
                "context_build": 5,
            },
        )
        with tempfile.TemporaryDirectory() as tmpdir:
            output_dir = Path(tmpdir)

            paths = write_eval_report([result], output_dir)

            self.assertTrue(paths["json"].exists())
            self.assertTrue(paths["markdown"].exists())
            payload = json.loads(paths["json"].read_text(encoding="utf-8"))
            markdown = paths["markdown"].read_text(encoding="utf-8")
            self.assertEqual(payload["summary"]["passed_count"], 1)
            self.assertEqual(payload["results"][0]["retrieval_backend"], "remote")
            self.assertEqual(payload["results"][0]["embedding_backend"], "hash")
            self.assertEqual(payload["results"][0]["vector_store_backend"], "remote")
            self.assertEqual(payload["results"][0]["reranker_backend"], "keyword-tech-weighted")
            self.assertEqual(payload["results"][0]["plan_route"], "tool")
            self.assertEqual(
                payload["results"][0]["plan_steps"],
                ["retrieve_context", "restart_mock_service", "answer_with_tool_results"],
            )
            self.assertEqual(payload["results"][0]["selected_tool"], "restart_mock_service")
            self.assertEqual(payload["results"][0]["recovery_action"], "retry_repaired_action")
            self.assertEqual(
                payload["results"][0]["replan_steps"],
                ["retry_repaired_action", "restart_mock_service", "answer_with_tool_results"],
            )
            self.assertEqual(payload["results"][0]["retrieval_stage_latency_ms"]["retrieval"], 42)
            self.assertIn("Retrieval backend: `remote`", markdown)
            self.assertIn("Embedding backend: `hash`", markdown)
            self.assertIn("Vector store backend: `remote`", markdown)
            self.assertIn("Reranker backend: `keyword-tech-weighted`", markdown)
            self.assertIn("Retrieval stage latency: `retrieval=42ms, coarse_rerank=8ms, bge_rerank=31ms, context_build=5ms`", markdown)
            self.assertIn("Agent task success rate: 100.00%", markdown)
            self.assertIn("Plan route: `tool`", markdown)
            self.assertIn("Plan steps: `retrieve_context > restart_mock_service > answer_with_tool_results`", markdown)
            self.assertIn("Node trace: `intent > retrieve > plan > tool_router > tool_exec > answer`", markdown)
            self.assertIn("Selected tool: `restart_mock_service`", markdown)
            self.assertIn("Tool actions: `restart_mock_service`", markdown)
            self.assertIn("Recovery action: `retry_repaired_action`", markdown)
            self.assertIn("Replan steps: `retry_repaired_action > restart_mock_service > answer_with_tool_results`", markdown)

    def test_report_summarizes_backend_comparison_dimension(self) -> None:
        results = [
            EvalResult(
                id="redis-1",
                query="q1",
                expected_source="redis-redis-issues-1.md",
                top_source="redis-redis-issues-1.md",
                source_names=["redis-redis-issues-1.md"],
                answer_preview="answer",
                checks={"source_hit": True, "top1_source": True, "keywords": True},
                keyword_hit_count=1,
                keyword_total=1,
                passed=True,
                retrieval_backend="in-memory",
                embedding_backend="hash",
                vector_store_backend="in-memory",
                reranker_backend="keyword-tech-weighted",
            ),
            EvalResult(
                id="redis-2",
                query="q2",
                expected_source="redis-redis-issues-2.md",
                top_source="wrong.md",
                source_names=["wrong.md"],
                answer_preview="answer",
                checks={"source_hit": False, "top1_source": False, "keywords": False},
                keyword_hit_count=0,
                keyword_total=1,
                passed=False,
                retrieval_backend="remote",
                embedding_backend="hash",
                vector_store_backend="remote",
                reranker_backend="keyword-tech-weighted",
            ),
        ]
        with tempfile.TemporaryDirectory() as tmpdir:
            output_dir = Path(tmpdir)

            paths = write_eval_report(results, output_dir)

            payload = json.loads(paths["json"].read_text(encoding="utf-8"))
            markdown = paths["markdown"].read_text(encoding="utf-8")
            self.assertEqual(len(payload["backend_comparison"]), 2)
            self.assertEqual(payload["backend_comparison"][0]["case_count"], 1)
            self.assertIn("## Backend Comparison", markdown)
            self.assertIn("Retrieval=`in-memory`", markdown)
            self.assertIn("Retrieval=`remote`", markdown)

    def test_report_summarizes_agent_path_dimension(self) -> None:
        results = [
            EvalResult(
                id="redis-1",
                query="q1",
                expected_source="redis-redis-issues-1.md",
                top_source="redis-redis-issues-1.md",
                source_names=["redis-redis-issues-1.md"],
                answer_preview="answer",
                checks={"source_hit": True, "top1_source": True, "keywords": True},
                keyword_hit_count=1,
                keyword_total=1,
                passed=True,
                plan_route="answer",
                plan_steps=["retrieve_context", "answer_with_context"],
                node_trace=["intent", "retrieve", "plan", "answer"],
            ),
            EvalResult(
                id="redis-2",
                query="q2",
                expected_source="redis-redis-issues-2.md",
                top_source="wrong.md",
                source_names=["wrong.md"],
                answer_preview="answer",
                checks={"source_hit": False, "top1_source": False, "keywords": False},
                keyword_hit_count=0,
                keyword_total=1,
                passed=False,
                plan_route="tool",
                plan_steps=["retrieve_context", "restart_mock_service", "answer_with_tool_results"],
                node_trace=["intent", "retrieve", "plan", "tool_router", "tool_exec", "answer"],
                selected_tool="restart_mock_service",
                tool_actions=[{"tool_name": "restart_mock_service", "tool_input": {"service_name": "redis"}}],
                recovery_action="degrade_to_answer",
                replan_steps=["degrade_to_answer", "answer_with_available_context"],
            ),
        ]
        with tempfile.TemporaryDirectory() as tmpdir:
            output_dir = Path(tmpdir)

            paths = write_eval_report(results, output_dir)

            payload = json.loads(paths["json"].read_text(encoding="utf-8"))
            markdown = paths["markdown"].read_text(encoding="utf-8")
            self.assertEqual(len(payload["agent_path_comparison"]), 2)
            self.assertEqual(payload["agent_path_comparison"][0]["case_count"], 1)
            self.assertIn("## Agent Path Comparison", markdown)
            self.assertIn("Plan=`answer`", markdown)
            self.assertIn("Plan=`tool`", markdown)
            self.assertIn("Tool=`restart_mock_service`", markdown)
            self.assertIn("Replan=`degrade_to_answer > answer_with_available_context`", markdown)


if __name__ == "__main__":
    unittest.main()
