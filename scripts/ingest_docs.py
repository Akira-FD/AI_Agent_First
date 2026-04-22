from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.config.settings import AppSettings
from app.rag.ingest_pipeline import IngestPipeline
from app.repositories.sqlite_repo import SQLiteRepository


def main() -> None:
    settings = AppSettings.from_root(ROOT)
    repository = SQLiteRepository(settings.sqlite_path)
    result = IngestPipeline(settings=settings, repository=repository).ingest_directory(settings.docs_dir)
    print(f"Ingested {result.document_count} documents and {result.chunk_count} chunks.")


if __name__ == "__main__":
    main()
