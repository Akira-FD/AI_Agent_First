from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class AppSettings:
    root_dir: Path
    app_name: str
    data_dir: Path
    docs_dir: Path
    cache_dir: Path
    sqlite_path: Path
    retrieval_top_k: int
    recent_message_limit: int

    @classmethod
    def from_root(cls, root_dir: Path) -> "AppSettings":
        data_dir = root_dir / "data"
        docs_dir = data_dir / "docs"
        cache_dir = data_dir / "cache"
        sqlite_dir = data_dir / "sqlite"
        for path in (data_dir, docs_dir, cache_dir, sqlite_dir):
            path.mkdir(parents=True, exist_ok=True)
        return cls(
            root_dir=root_dir,
            app_name="AI Agent First",
            data_dir=data_dir,
            docs_dir=docs_dir,
            cache_dir=cache_dir,
            sqlite_path=sqlite_dir / "app.db",
            retrieval_top_k=int(os.getenv("AI_AGENT_FIRST_TOP_K", "5")),
            recent_message_limit=int(os.getenv("AI_AGENT_FIRST_RECENT_MESSAGE_LIMIT", "8")),
        )
