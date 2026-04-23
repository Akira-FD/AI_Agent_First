from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class GithubHarvestConfig:
    repositories: list[str]
    topic_keywords: list[str]
    min_repo_stars: int = 1000
    min_reply_score: int = 3
    max_items: int = 50
    include_issues: bool = True
    include_discussions: bool = True

    def __post_init__(self) -> None:
        if not self.repositories:
            raise ValueError("At least one GitHub repository is required.")
        if not self.topic_keywords:
            raise ValueError("At least one topic keyword is required.")
        if self.min_reply_score < 0:
            raise ValueError("min_reply_score cannot be negative.")
        if self.max_items <= 0:
            raise ValueError("max_items must be greater than zero.")


@dataclass(frozen=True)
class GithubReplyRecord:
    author: str
    body: str
    url: str
    reactions: dict[str, int] = field(default_factory=dict)
    is_author_association_trusted: bool = False
    is_accepted_answer: bool = False

    @property
    def quality_score(self) -> int:
        positive = self.reactions.get("+1", 0) + self.reactions.get("heart", 0) + self.reactions.get("hooray", 0)
        trust_bonus = 3 if self.is_author_association_trusted else 0
        accepted_bonus = 5 if self.is_accepted_answer else 0
        return positive + trust_bonus + accepted_bonus


@dataclass(frozen=True)
class GithubIssueRecord:
    repository: str
    number: int
    title: str
    body: str
    url: str
    labels: list[str]
    state: str
    repo_stars: int
    replies: list[GithubReplyRecord] = field(default_factory=list)


@dataclass(frozen=True)
class GithubKnowledgeDocument:
    slug: str
    source_filename: str
    title: str
    markdown: str
    provenance_url: str
    answer_keywords: list[str]
