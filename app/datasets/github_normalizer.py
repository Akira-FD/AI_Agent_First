from __future__ import annotations

import re

from app.datasets.github_models import GithubIssueRecord, GithubKnowledgeDocument, GithubReplyRecord


class GithubKnowledgeNormalizer:
    def __init__(self, min_reply_score: int = 3, max_replies: int = 3) -> None:
        self.min_reply_score = min_reply_score
        self.max_replies = max_replies

    def normalize_issue(self, issue: GithubIssueRecord) -> GithubKnowledgeDocument:
        slug = self._slugify(f"{issue.repository}-issues-{issue.number}")
        selected_replies = self._select_replies(issue.replies)
        answer_text = "\n\n".join(reply.body.strip() for reply in selected_replies)
        markdown = self._render_markdown(issue, selected_replies)
        return GithubKnowledgeDocument(
            slug=slug,
            source_filename=f"{slug}.md",
            title=issue.title,
            markdown=markdown,
            provenance_url=issue.url,
            answer_keywords=self._extract_keywords(answer_text),
        )

    def _select_replies(self, replies: list[GithubReplyRecord]) -> list[GithubReplyRecord]:
        high_signal = [reply for reply in replies if reply.quality_score >= self.min_reply_score and reply.body.strip()]
        high_signal.sort(key=lambda reply: reply.quality_score, reverse=True)
        return high_signal[: self.max_replies]

    def _render_markdown(self, issue: GithubIssueRecord, replies: list[GithubReplyRecord]) -> str:
        labels = ", ".join(issue.labels) if issue.labels else "none"
        reply_sections = []
        for index, reply in enumerate(replies, start=1):
            reply_sections.append(
                "\n".join(
                    [
                        f"### High Signal Answer {index}",
                        "",
                        reply.body.strip(),
                        "",
                        f"- Author: {reply.author}",
                        f"- Quality score: {reply.quality_score}",
                        f"- URL: {reply.url}",
                    ]
                )
            )

        return "\n\n".join(
            [
                f"# {issue.title}",
                "",
                "## GitHub Provenance",
                "",
                f"- Repository: {issue.repository}",
                f"- Issue: #{issue.number}",
                f"- State: {issue.state}",
                f"- Labels: {labels}",
                f"- Repository stars: {issue.repo_stars}",
                f"- URL: {issue.url}",
                "",
                "## Problem",
                "",
                issue.body.strip(),
                "",
                "## Curated Answers",
                "",
                "\n\n".join(reply_sections) if reply_sections else "No high-signal answer selected.",
            ]
        ).strip() + "\n"

    def _extract_keywords(self, text: str) -> list[str]:
        latin_terms = re.findall(r"[A-Za-z][A-Za-z0-9_-]{2,}", text)
        seen: set[str] = set()
        keywords: list[str] = []
        for term in latin_terms:
            normalized = term.lower()
            if normalized not in seen:
                seen.add(normalized)
                keywords.append(term)
            if len(keywords) >= 8:
                break
        return keywords

    def _slugify(self, value: str) -> str:
        return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
