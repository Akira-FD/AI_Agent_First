import json
import tempfile
import unittest
from pathlib import Path

from app.datasets.github_client import GithubApiRateLimitError, GithubRestClient


class GithubClientErrorTests(unittest.TestCase):
    def test_cache_path_generation_is_stable(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            client = GithubRestClient(cache_dir=Path(tmpdir))
            path = client._cache_path("https://api.github.com/repos/redis/redis")
            self.assertTrue(str(path).endswith(".json"))

    def test_rate_limit_error_can_be_serialized_for_summary(self) -> None:
        error = GithubApiRateLimitError("rate limited", reset_at="2026-04-24T00:00:00Z")

        payload = {"error": str(error), "reset_at": error.reset_at}

        self.assertEqual(json.loads(json.dumps(payload)), payload)


if __name__ == "__main__":
    unittest.main()
