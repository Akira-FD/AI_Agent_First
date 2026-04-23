from __future__ import annotations

import json
from pathlib import Path

from app.datasets.github_models import GithubKnowledgeDocument


class GithubDatasetWriter:
    def write_documents(self, documents: list[GithubKnowledgeDocument], docs_dir: Path) -> list[Path]:
        docs_dir.mkdir(parents=True, exist_ok=True)
        written: list[Path] = []
        for document in documents:
            path = docs_dir / document.source_filename
            path.write_text(document.markdown, encoding="utf-8")
            written.append(path)
        return written

    def write_eval_cases(self, cases: list[dict[str, object]], output_path: Path) -> Path:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(json.dumps(cases, ensure_ascii=False, indent=2), encoding="utf-8")
        return output_path
