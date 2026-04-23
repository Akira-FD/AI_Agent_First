import json
import tempfile
import unittest
from pathlib import Path

from app.datasets.github_models import GithubKnowledgeDocument
from app.datasets.github_writer import GithubDatasetWriter


class GithubDatasetWriterTests(unittest.TestCase):
    def test_writes_documents_and_eval_cases_to_disk(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            document = GithubKnowledgeDocument(
                slug="redis-redis-issues-1",
                source_filename="redis-redis-issues-1.md",
                title="Redis timeout",
                markdown="# Redis timeout\n\n## Answer\n\nCheck slowlog.\n",
                provenance_url="https://github.com/redis/redis/issues/1",
                answer_keywords=["slowlog"],
            )
            cases = [
                {
                    "id": "redis-redis-issues-1",
                    "query": "How should I handle Redis timeout?",
                    "expected_source": "redis-redis-issues-1.md",
                    "answer_keywords": ["slowlog"],
                }
            ]

            writer = GithubDatasetWriter()
            doc_paths = writer.write_documents([document], root / "docs")
            cases_path = writer.write_eval_cases(cases, root / "eval" / "github_cases.json")

            self.assertEqual(doc_paths[0].read_text(encoding="utf-8"), document.markdown)
            self.assertEqual(json.loads(cases_path.read_text(encoding="utf-8")), cases)


if __name__ == "__main__":
    unittest.main()
