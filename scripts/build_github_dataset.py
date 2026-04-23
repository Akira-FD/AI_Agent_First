from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.datasets.github_case_builder import GithubEvalCaseBuilder
from app.datasets.github_client import GithubApiRateLimitError, GithubRestClient
from app.datasets.github_harvester import GithubHarvester
from app.datasets.github_models import GithubHarvestConfig
from app.datasets.github_case_builder import GithubEvalCaseBuilder
from app.datasets.github_models import GithubIssueRecord, GithubReplyRecord
from app.datasets.github_normalizer import GithubKnowledgeNormalizer
from app.datasets.github_writer import GithubDatasetWriter


DEFAULT_REPOSITORIES = [
    "redis/redis",
    "mysql/mysql-server",
    "kubernetes/kubernetes",
    "prometheus/prometheus",
    "elastic/elasticsearch",
    "nginx/nginx",
]

DEFAULT_KEYWORDS = [
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
]


def build_sample_records() -> list[GithubIssueRecord]:
    return [
        GithubIssueRecord(
            repository="redis/redis",
            number=1001,
            title="Redis timeout after memory pressure",
            body="Redis requests time out after memory usage grows quickly.",
            url="https://github.com/redis/redis/issues/1001",
            labels=["question", "memory"],
            state="closed",
            repo_stars=70000,
            replies=[
                GithubReplyRecord(
                    author="maintainer",
                    body="Check used_memory, maxmemory policy, slowlog, and client connection count before restarting Redis.",
                    url="https://github.com/redis/redis/issues/1001#issuecomment-1",
                    reactions={"+1": 12, "heart": 2},
                    is_author_association_trusted=True,
                )
            ],
        )
    ]


def main() -> None:
    parser = argparse.ArgumentParser(description="Build GitHub-derived knowledge docs and eval cases.")
    parser.add_argument("--sample", action="store_true", help="Generate a small offline sample dataset.")
    parser.add_argument("--real", action="store_true", help="Harvest real GitHub issues/comments into docs and eval cases.")
    parser.add_argument("--docs-dir", default=str(ROOT / "data" / "docs" / "github"))
    parser.add_argument("--cases-path", default=str(ROOT / "evaluation" / "cases" / "github_cases.json"))
    parser.add_argument("--cache-dir", default=str(ROOT / "data" / "cache" / "github_api"))
    parser.add_argument("--target-count", type=int, default=100)
    parser.add_argument("--min-repo-stars", type=int, default=5000)
    parser.add_argument("--min-reply-score", type=int, default=4)
    parser.add_argument("--repositories", default=",".join(DEFAULT_REPOSITORIES))
    parser.add_argument("--keywords", default=",".join(DEFAULT_KEYWORDS))
    parser.add_argument("--summary-path", default=str(ROOT / "evaluation" / "reports" / "github_dataset_summary.json"))
    args = parser.parse_args()

    writer = GithubDatasetWriter()

    if args.sample:
        normalizer = GithubKnowledgeNormalizer(min_reply_score=3)
        documents = [normalizer.normalize_issue(record) for record in build_sample_records()]
        cases = GithubEvalCaseBuilder().build_cases(documents)
        doc_paths = writer.write_documents(documents, Path(args.docs_dir))
        cases_path = writer.write_eval_cases(cases, Path(args.cases_path))
        print(f"Wrote {len(doc_paths)} GitHub knowledge document(s) to {args.docs_dir}")
        print(f"Wrote {len(cases)} eval case(s) to {cases_path}")
        return

    if not args.real:
        raise SystemExit("Choose either --sample or --real.")

    repositories = [item.strip() for item in args.repositories.split(",") if item.strip()]
    keywords = [item.strip() for item in args.keywords.split(",") if item.strip()]
    config = GithubHarvestConfig(
        repositories=repositories,
        topic_keywords=keywords,
        min_repo_stars=args.min_repo_stars,
        min_reply_score=args.min_reply_score,
        max_items=args.target_count,
    )

    token = os.getenv("GITHUB_TOKEN")
    client = GithubRestClient(token=token, cache_dir=Path(args.cache_dir))
    harvester = GithubHarvester(client)
    normalizer = GithubKnowledgeNormalizer(min_reply_score=args.min_reply_score)
    error: dict[str, str] | None = None
    try:
        records = harvester.harvest(config)
    except GithubApiRateLimitError as exc:
        records = []
        error = {
            "type": "rate_limit",
            "message": str(exc),
            "reset_at": exc.reset_at,
            "hint": "Set GITHUB_TOKEN and rerun this command to reliably generate about 100 cases.",
        }
    documents = [normalizer.normalize_issue(record) for record in records]
    cases = GithubEvalCaseBuilder().build_cases(documents)
    doc_paths = writer.write_documents(documents, Path(args.docs_dir))
    cases_path = writer.write_eval_cases(cases, Path(args.cases_path))

    summary = {
        "requested_target_count": args.target_count,
        "harvested_records": len(records),
        "documents_written": len(doc_paths),
        "cases_written": len(cases),
        "repositories": repositories,
        "keywords": keywords,
        "token_present": bool(token),
    }
    if error:
        summary["error"] = error
    summary_path = Path(args.summary_path)
    summary_path.parent.mkdir(parents=True, exist_ok=True)
    summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    print(f"Wrote knowledge docs to {args.docs_dir}")
    print(f"Wrote eval cases to {cases_path}")


if __name__ == "__main__":
    main()
