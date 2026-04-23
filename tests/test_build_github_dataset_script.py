import tempfile
import unittest
from pathlib import Path

from app.datasets.github_harvester import GithubHarvester
from app.datasets.github_models import GithubHarvestConfig
from app.datasets.github_normalizer import GithubKnowledgeNormalizer
from app.datasets.github_writer import GithubDatasetWriter


class FakeGithubClientForScript:
    def get_repository(self, repository: str):
        return {"stargazers_count": 70000}

    def search_issues(self, query, per_page: int = 10):
        return {
            "items": [
                {
                    "number": 1,
                    "title": f"{query.keyword} troubleshooting",
                    "body": f"How to solve {query.keyword}?",
                    "html_url": f"https://github.com/{query.repository}/issues/1",
                    "labels": [{"name": "question"}],
                    "state": "closed",
                }
            ]
        }

    def list_issue_comments(self, repository: str, issue_number: int):
        return [
            {
                "user": {"login": "maintainer"},
                "body": "Check logs, resource usage, and recent config changes.",
                "html_url": f"https://github.com/{repository}/issues/{issue_number}#issuecomment-1",
                "author_association": "MEMBER",
                "reactions": {"+1": 6},
            }
        ]


class BuildGithubDatasetScriptTests(unittest.TestCase):
    def test_pipeline_can_build_documents_and_cases_from_real_harvest_components(self) -> None:
        config = GithubHarvestConfig(
            repositories=["redis/redis"],
            topic_keywords=["redis timeout", "redis oom"],
            max_items=5,
            min_repo_stars=1000,
            min_reply_score=3,
        )
        harvester = GithubHarvester(FakeGithubClientForScript())
        normalizer = GithubKnowledgeNormalizer(min_reply_score=3)
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            writer = GithubDatasetWriter()
            records = harvester.harvest(config)
            documents = [normalizer.normalize_issue(record) for record in records]
            cases = __import__("app.datasets.github_case_builder", fromlist=["GithubEvalCaseBuilder"]).GithubEvalCaseBuilder().build_cases(documents)
            doc_paths = writer.write_documents(documents, root / "docs")
            cases_path = writer.write_eval_cases(cases, root / "cases.json")

            self.assertTrue(doc_paths)
            self.assertTrue(cases_path.exists())


if __name__ == "__main__":
    unittest.main()
