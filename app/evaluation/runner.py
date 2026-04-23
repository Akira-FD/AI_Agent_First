from __future__ import annotations

from app.evaluation.graders import grade_response
from app.evaluation.models import EvalCase, EvalResult


class EvaluationRunner:
    def __init__(self, agent) -> None:
        self.agent = agent

    def run_cases(self, cases: list[EvalCase]) -> list[EvalResult]:
        results: list[EvalResult] = []
        for index, case in enumerate(cases, start=1):
            response = self.agent.run(session_id=f"eval-{index}", user_query=case.query)
            results.append(grade_response(case, response))
        return results
