from __future__ import annotations
# ruff: noqa: E402

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.config.settings import AppSettings
from app.rag.ingest_pipeline import IngestPipeline
from app.rag.vector_store import build_vector_store
from app.repositories.sqlite_repo import SQLiteRepository


def main() -> None:
    settings = AppSettings.from_root(ROOT)
    repository = SQLiteRepository(settings.sqlite_path)
    vector_store = build_vector_store(settings)
    result = IngestPipeline(
        settings=settings,
        repository=repository,
        vector_indexer=vector_store,
    ).ingest_directory(settings.docs_dir)
    print(
        f"Ingested {result.document_count} documents, {result.chunk_count} chunks, "
        f"indexed {result.indexed_chunk_count} chunks."
    )


if __name__ == "__main__":
    main()
