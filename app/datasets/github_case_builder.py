from __future__ import annotations

from app.datasets.github_models import GithubKnowledgeDocument


class GithubEvalCaseBuilder:
    def build_cases(self, documents: list[GithubKnowledgeDocument]) -> list[dict[str, object]]:
        cases: list[dict[str, object]] = []
        for document in documents:
            query_title = document.title
            if query_title.lower().startswith("how to "):
                query = query_title
            else:
                query = f"How should I handle: {query_title}"
            cases.append(
                {
                    "id": document.slug,
                    "query": query,
                    "expected_source": document.source_filename,
                    "answer_keywords": document.answer_keywords,
                    "provenance_url": document.provenance_url,
                }
            )
        return cases
