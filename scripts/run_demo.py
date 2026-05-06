from __future__ import annotations
# ruff: noqa: E402

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.main import bootstrap_application
from app.rag.ingest_pipeline import IngestPipeline


def main() -> None:
    app = bootstrap_application(ROOT)
    IngestPipeline(
        settings=app.settings,
        repository=app.repository,
        vector_indexer=app.vector_store,
    ).ingest_directory(app.settings.docs_dir)
    response = app.agent.run(session_id="demo", user_query="请帮我重启 redis 服务")
    print(response.answer)
    print("Sources:", response.sources)
    print("Tool logs:", response.tool_logs)


if __name__ == "__main__":
    main()
