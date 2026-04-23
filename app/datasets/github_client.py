from __future__ import annotations

import json
import os
from pathlib import Path
import urllib.parse
import urllib.request
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any
from urllib.error import HTTPError


class GithubApiError(RuntimeError):
    pass


class GithubApiRateLimitError(GithubApiError):
    def __init__(self, message: str, reset_at: str = "") -> None:
        super().__init__(message)
        self.reset_at = reset_at


@dataclass(frozen=True)
class GithubSearchQuery:
    repository: str
    keyword: str
    state: str = "closed"
    sort: str = "reactions"
    order: str = "desc"


class GithubRestClient:
    """Small REST client wrapper designed for dependency injection and offline tests."""

    base_url = "https://api.github.com"

    def __init__(self, token: str | None = None, timeout: int = 30, cache_dir: Path | None = None) -> None:
        self.token = token or os.getenv("GITHUB_TOKEN")
        self.timeout = timeout
        self.cache_dir = cache_dir

    def search_issues(self, query: GithubSearchQuery, per_page: int = 10) -> dict[str, Any]:
        q = f'repo:{query.repository} is:issue state:{query.state} "{query.keyword}"'
        params = urllib.parse.urlencode(
            {
                "q": q,
                "sort": query.sort,
                "order": query.order,
                "per_page": per_page,
            }
        )
        return self._get_json(f"{self.base_url}/search/issues?{params}")

    def get_repository(self, repository: str) -> dict[str, Any]:
        return self._get_json(f"{self.base_url}/repos/{repository}")

    def list_issue_comments(self, repository: str, issue_number: int) -> list[dict[str, Any]]:
        return self._get_json(f"{self.base_url}/repos/{repository}/issues/{issue_number}/comments")

    def _get_json(self, url: str) -> Any:
        cache_path = self._cache_path(url)
        if cache_path and cache_path.exists():
            return json.loads(cache_path.read_text(encoding="utf-8"))

        headers = {
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": "AI-Agent-First-MVP",
        }
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        request = urllib.request.Request(url, headers=headers)
        try:
            with urllib.request.urlopen(request, timeout=self.timeout) as response:
                payload = json.loads(response.read().decode("utf-8"))
        except HTTPError as exc:
            if exc.code in (403, 429):
                reset_header = exc.headers.get("x-ratelimit-reset", "")
                reset_at = self._format_reset_time(reset_header)
                raise GithubApiRateLimitError(f"GitHub API rate limit exceeded for {url}", reset_at=reset_at) from exc
            raise GithubApiError(f"GitHub API request failed with HTTP {exc.code}: {url}") from exc
        if cache_path:
            cache_path.parent.mkdir(parents=True, exist_ok=True)
            cache_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        return payload

    def _cache_path(self, url: str) -> Path | None:
        if self.cache_dir is None:
            return None
        encoded = urllib.parse.quote(url, safe="")
        return self.cache_dir / f"{encoded}.json"

    def _format_reset_time(self, reset_header: str) -> str:
        if not reset_header:
            return ""
        try:
            return datetime.fromtimestamp(int(reset_header), tz=timezone.utc).isoformat()
        except ValueError:
            return ""
