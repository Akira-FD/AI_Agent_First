from __future__ import annotations

from app.datasets.github_client import GithubSearchQuery
from app.datasets.github_models import GithubHarvestConfig, GithubIssueRecord, GithubReplyRecord


TRUSTED_ASSOCIATIONS = {"OWNER", "MEMBER", "COLLABORATOR"}
LOW_SIGNAL_LABEL_KEYWORDS = {
    "feature",
    "enhancement",
    "proposal",
    "design",
}
OPERATIONS_HINT_KEYWORDS = {
    "timeout",
    "oom",
    "connection refused",
    "restart",
    "slow query",
    "memory pressure",
    "latency",
    "crashloopbackoff",
    "logs",
    "health check",
    "error",
    "crash",
    "slow",
    "memory",
    "connection",
}


class GithubHarvester:
    def __init__(self, client) -> None:
        self.client = client

    def harvest(self, config: GithubHarvestConfig) -> list[GithubIssueRecord]:
        repository_stars = {
            repository: self.client.get_repository(repository).get("stargazers_count", 0)
            for repository in config.repositories
        }
        harvested: list[GithubIssueRecord] = []
        seen: set[tuple[str, int]] = set()

        for repository in config.repositories:
            if repository_stars[repository] < config.min_repo_stars:
                continue
            for keyword in config.topic_keywords:
                search_result = self.client.search_issues(
                    GithubSearchQuery(repository=repository, keyword=keyword),
                    per_page=min(config.max_items, 25),
                )
                for item in search_result.get("items", []):
                    issue_key = (repository, item["number"])
                    if issue_key in seen:
                        continue
                    if not self._is_operationally_relevant(item):
                        continue
                    seen.add(issue_key)
                    replies = self._load_replies(repository, item["number"], config.min_reply_score)
                    if not replies:
                        continue
                    harvested.append(
                        GithubIssueRecord(
                            repository=repository,
                            number=item["number"],
                            title=item.get("title", ""),
                            body=item.get("body", "") or "",
                            url=item.get("html_url", ""),
                            labels=[label["name"] for label in item.get("labels", []) if "name" in label],
                            state=item.get("state", "open"),
                            repo_stars=repository_stars[repository],
                            replies=replies,
                        )
                    )
                    if len(harvested) >= config.max_items:
                        return harvested[: config.max_items]

        return harvested[: config.max_items]

    def _load_replies(self, repository: str, issue_number: int, min_reply_score: int) -> list[GithubReplyRecord]:
        replies: list[GithubReplyRecord] = []
        for comment in self.client.list_issue_comments(repository, issue_number):
            reply = GithubReplyRecord(
                author=comment.get("user", {}).get("login", "unknown"),
                body=comment.get("body", "") or "",
                url=comment.get("html_url", ""),
                reactions=comment.get("reactions", {}) or {},
                is_author_association_trusted=comment.get("author_association", "") in TRUSTED_ASSOCIATIONS,
            )
            if reply.quality_score >= min_reply_score and reply.body.strip():
                replies.append(reply)
        replies.sort(key=lambda item: item.quality_score, reverse=True)
        return replies

    def _is_operationally_relevant(self, item: dict) -> bool:
        labels = [label.get("name", "").lower() for label in item.get("labels", [])]
        if any(any(keyword in label for keyword in LOW_SIGNAL_LABEL_KEYWORDS) for label in labels):
            title = (item.get("title", "") or "").lower()
            body = (item.get("body", "") or "").lower()
            if not any(keyword in title or keyword in body for keyword in OPERATIONS_HINT_KEYWORDS):
                return False

        title = (item.get("title", "") or "").lower()
        if title.startswith("feature request") or title.startswith("[feature]"):
            return False
        return True
