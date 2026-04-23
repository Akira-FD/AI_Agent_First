import unittest

from app.datasets.github_case_builder import GithubEvalCaseBuilder
from app.datasets.github_models import GithubHarvestConfig, GithubIssueRecord, GithubReplyRecord
from app.datasets.github_normalizer import GithubKnowledgeNormalizer


class GithubDatasetArchitectureTests(unittest.TestCase):
    def test_harvest_config_validates_minimum_quality_thresholds(self) -> None:
        config = GithubHarvestConfig(
            repositories=["redis/redis"],
            topic_keywords=["redis timeout", "redis oom"],
            min_repo_stars=1000,
            min_reply_score=3,
            max_items=20,
        )

        self.assertEqual(config.repositories, ["redis/redis"])
        self.assertEqual(config.min_reply_score, 3)
        self.assertEqual(config.max_items, 20)

    def test_normalizer_turns_high_signal_issue_into_markdown_document(self) -> None:
        issue = GithubIssueRecord(
            repository="redis/redis",
            number=123,
            title="Redis timeout after memory pressure",
            body="Redis returns timeout when memory grows quickly.",
            url="https://github.com/redis/redis/issues/123",
            labels=["question"],
            state="closed",
            repo_stars=70000,
            replies=[
                GithubReplyRecord(
                    author="maintainer",
                    body="Check used_memory, maxmemory policy, and slowlog before restarting Redis.",
                    url="https://github.com/redis/redis/issues/123#issuecomment-1",
                    reactions={"+1": 8, "heart": 2},
                    is_author_association_trusted=True,
                ),
                GithubReplyRecord(
                    author="random",
                    body="Same problem.",
                    url="https://github.com/redis/redis/issues/123#issuecomment-2",
                    reactions={"+1": 0},
                    is_author_association_trusted=False,
                ),
            ],
        )

        document = GithubKnowledgeNormalizer(min_reply_score=3).normalize_issue(issue)

        self.assertEqual(document.slug, "redis-redis-issues-123")
        self.assertIn("# Redis timeout after memory pressure", document.markdown)
        self.assertIn("Check used_memory", document.markdown)
        self.assertIn("GitHub Provenance", document.markdown)
        self.assertNotIn("Same problem", document.markdown)

    def test_case_builder_derives_rag_cases_from_normalized_documents(self) -> None:
        issue = GithubIssueRecord(
            repository="redis/redis",
            number=456,
            title="How to debug Redis OOM timeout?",
            body="What should I check when Redis has OOM and timeout?",
            url="https://github.com/redis/redis/issues/456",
            labels=["question"],
            state="closed",
            repo_stars=70000,
            replies=[
                GithubReplyRecord(
                    author="maintainer",
                    body="Inspect maxmemory, eviction policy, slowlog, and client connections.",
                    url="https://github.com/redis/redis/issues/456#issuecomment-1",
                    reactions={"+1": 12},
                    is_author_association_trusted=True,
                )
            ],
        )
        document = GithubKnowledgeNormalizer(min_reply_score=3).normalize_issue(issue)

        cases = GithubEvalCaseBuilder().build_cases([document])

        self.assertEqual(len(cases), 1)
        self.assertEqual(cases[0]["expected_source"], "redis-redis-issues-456.md")
        self.assertIn("Redis OOM timeout", cases[0]["query"])
        self.assertIn("maxmemory", cases[0]["answer_keywords"])
        self.assertEqual(cases[0]["expected_plan_route"], "answer")
        self.assertEqual(cases[0]["expected_plan_steps"], ["retrieve_context", "answer_with_context"])
        self.assertEqual(cases[0]["expected_tool_names"], [])
        self.assertEqual(cases[0]["expected_recovery_action"], "")
        self.assertEqual(cases[0]["expected_replan_steps"], [])


if __name__ == "__main__":
    unittest.main()
