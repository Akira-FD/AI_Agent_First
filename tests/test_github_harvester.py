import unittest

from app.datasets.github_harvester import GithubHarvester
from app.datasets.github_models import GithubHarvestConfig


class FakeGithubClient:
    def __init__(self) -> None:
        self.repo_stars = {
            "redis/redis": 70000,
            "tiny/repo": 2,
        }
        self.comments = {
            ("redis/redis", 1): [
                {
                    "user": {"login": "maintainer"},
                    "body": "Check maxmemory, slowlog, client connections, and memory fragmentation.",
                    "html_url": "https://github.com/redis/redis/issues/1#issuecomment-1",
                    "author_association": "MEMBER",
                    "reactions": {"+1": 9, "heart": 1},
                },
                {
                    "user": {"login": "noisy-user"},
                    "body": "same here",
                    "html_url": "https://github.com/redis/redis/issues/1#issuecomment-2",
                    "author_association": "NONE",
                    "reactions": {"+1": 0},
                },
            ],
            ("redis/redis", 2): [
                {
                    "user": {"login": "triager"},
                    "body": "Restart only after checking persistence and active writes.",
                    "html_url": "https://github.com/redis/redis/issues/2#issuecomment-1",
                    "author_association": "COLLABORATOR",
                    "reactions": {"+1": 5},
                }
            ],
            ("tiny/repo", 9): [
                {
                    "user": {"login": "owner"},
                    "body": "Good answer but repo is too small.",
                    "html_url": "https://github.com/tiny/repo/issues/9#issuecomment-1",
                    "author_association": "OWNER",
                    "reactions": {"+1": 10},
                }
            ],
        }

    def get_repository(self, repository: str):
        return {"stargazers_count": self.repo_stars[repository]}

    def search_issues(self, query, per_page: int = 10):
        if query.repository == "tiny/repo":
            return {
                "items": [
                    {
                        "number": 9,
                        "title": "Tiny repo issue",
                        "body": "Should be filtered by repo stars.",
                        "html_url": "https://github.com/tiny/repo/issues/9",
                        "labels": [{"name": "question"}],
                        "state": "closed",
                    }
                ]
            }
        return {
            "items": [
                {
                    "number": 1,
                    "title": "Redis OOM timeout",
                    "body": "Redis times out under memory pressure.",
                    "html_url": "https://github.com/redis/redis/issues/1",
                    "labels": [{"name": "question"}],
                    "state": "closed",
                },
                {
                    "number": 2,
                    "title": "Redis restart safety",
                    "body": "When is restart safe?",
                    "html_url": "https://github.com/redis/redis/issues/2",
                    "labels": [{"name": "question"}],
                    "state": "closed",
                },
                {
                    "number": 1,
                    "title": "Duplicate Redis OOM timeout",
                    "body": "Duplicate should be removed.",
                    "html_url": "https://github.com/redis/redis/issues/1",
                    "labels": [{"name": "question"}],
                    "state": "closed",
                },
            ]
        }

    def list_issue_comments(self, repository: str, issue_number: int):
        return self.comments[(repository, issue_number)]


class GithubHarvesterTests(unittest.TestCase):
    def test_harvests_high_signal_issues_with_comments_dedupe_and_star_filter(self) -> None:
        config = GithubHarvestConfig(
            repositories=["redis/redis", "tiny/repo"],
            topic_keywords=["redis timeout", "restart"],
            min_repo_stars=1000,
            min_reply_score=3,
            max_items=5,
        )

        records = GithubHarvester(FakeGithubClient()).harvest(config)

        self.assertEqual([record.number for record in records], [1, 2])
        self.assertEqual(records[0].repo_stars, 70000)
        self.assertEqual(len(records[0].replies), 1)
        self.assertEqual(records[0].replies[0].author, "maintainer")
        self.assertGreaterEqual(records[0].replies[0].quality_score, 3)

    def test_harvest_respects_max_items(self) -> None:
        config = GithubHarvestConfig(
            repositories=["redis/redis"],
            topic_keywords=["redis timeout", "restart"],
            min_repo_stars=1000,
            min_reply_score=3,
            max_items=1,
        )

        records = GithubHarvester(FakeGithubClient()).harvest(config)

        self.assertEqual(len(records), 1)

    def test_filters_feature_request_and_low_operational_relevance_items(self) -> None:
        client = FakeGithubClient()
        original_search = client.search_issues

        def search_with_feature_request(query, per_page: int = 10):
            result = original_search(query, per_page)
            result["items"].append(
                {
                    "number": 77,
                    "title": "Feature Request: Add new cluster pubsub mode",
                    "body": "Proposal for a new feature design.",
                    "html_url": "https://github.com/redis/redis/issues/77",
                    "labels": [{"name": "feature request"}],
                    "state": "closed",
                }
            )
            client.comments[("redis/redis", 77)] = [
                {
                    "user": {"login": "maintainer"},
                    "body": "Interesting design, but not an operations troubleshooting answer.",
                    "html_url": "https://github.com/redis/redis/issues/77#issuecomment-1",
                    "author_association": "MEMBER",
                    "reactions": {"+1": 8},
                }
            ]
            return result

        client.search_issues = search_with_feature_request
        config = GithubHarvestConfig(
            repositories=["redis/redis"],
            topic_keywords=["redis timeout"],
            min_repo_stars=1000,
            min_reply_score=3,
            max_items=10,
        )

        records = GithubHarvester(client).harvest(config)

        self.assertNotIn(77, [record.number for record in records])


if __name__ == "__main__":
    unittest.main()
