from __future__ import annotations

import sqlite3
from contextlib import closing
from datetime import datetime, timezone
import json
from pathlib import Path
import uuid

from app.models.document import DocumentChunk, DocumentRecord


class SQLiteRepository:
    def __init__(self, db_path: Path) -> None:
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._initialize()

    def _connect(self) -> sqlite3.Connection:
        return sqlite3.connect(self.db_path)

    def _initialize(self) -> None:
        with closing(self._connect()) as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS documents (
                    id TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    source TEXT,
                    path TEXT,
                    file_size INTEGER NOT NULL DEFAULT 0,
                    chunk_count INTEGER NOT NULL DEFAULT 0,
                    created_at TEXT NOT NULL DEFAULT '',
                    updated_at TEXT NOT NULL DEFAULT ''
                )
                """
            )
            self._ensure_columns(
                conn,
                "documents",
                {
                    "file_size": "INTEGER NOT NULL DEFAULT 0",
                    "chunk_count": "INTEGER NOT NULL DEFAULT 0",
                    "created_at": "TEXT NOT NULL DEFAULT ''",
                    "updated_at": "TEXT NOT NULL DEFAULT ''",
                },
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS document_chunks (
                    chunk_id TEXT PRIMARY KEY,
                    doc_id TEXT NOT NULL,
                    title TEXT NOT NULL,
                    section_path TEXT NOT NULL,
                    content TEXT NOT NULL,
                    source TEXT NOT NULL,
                    chunk_order INTEGER NOT NULL,
                    token_count INTEGER NOT NULL
                )
                """
                )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS chat_sessions (
                    session_id TEXT PRIMARY KEY,
                    title TEXT NOT NULL DEFAULT '',
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS chat_messages (
                    id TEXT PRIMARY KEY,
                    session_id TEXT NOT NULL,
                    role TEXT NOT NULL,
                    content TEXT NOT NULL,
                    created_at TEXT NOT NULL
                )
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS tool_logs (
                    id TEXT PRIMARY KEY,
                    session_id TEXT NOT NULL,
                    tool_name TEXT NOT NULL,
                    input_json TEXT NOT NULL,
                    output_json TEXT NOT NULL,
                    status TEXT NOT NULL,
                    created_at TEXT NOT NULL
                )
                """
            )
            conn.commit()

    def _ensure_columns(self, conn: sqlite3.Connection, table: str, columns: dict[str, str]) -> None:
        existing = {row[1] for row in conn.execute(f"PRAGMA table_info({table})").fetchall()}
        for name, definition in columns.items():
            if name not in existing:
                conn.execute(f"ALTER TABLE {table} ADD COLUMN {name} {definition}")

    def upsert_document(self, document: DocumentRecord) -> None:
        with closing(self._connect()) as conn:
            conn.execute(
                """
                INSERT INTO documents(id, title, source, path, file_size, chunk_count, created_at, updated_at)
                VALUES(?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                    title = excluded.title,
                    source = excluded.source,
                    path = excluded.path,
                    file_size = excluded.file_size,
                    chunk_count = excluded.chunk_count,
                    updated_at = excluded.updated_at
                """,
                (
                    document.id,
                    document.title,
                    document.source,
                    document.path,
                    document.file_size,
                    document.chunk_count,
                    document.created_at,
                    document.updated_at,
                ),
            )
            conn.commit()

    def delete_documents_by_path(self, path: str) -> None:
        with closing(self._connect()) as conn:
            rows = conn.execute("SELECT id FROM documents WHERE path = ?", (path,)).fetchall()
            doc_ids = [row[0] for row in rows]
            if doc_ids:
                conn.executemany("DELETE FROM document_chunks WHERE doc_id = ?", [(doc_id,) for doc_id in doc_ids])
                conn.execute("DELETE FROM documents WHERE path = ?", (path,))
            conn.commit()

    def replace_document_chunks(self, doc_id: str, chunks: list[DocumentChunk]) -> None:
        with closing(self._connect()) as conn:
            conn.execute("DELETE FROM document_chunks WHERE doc_id = ?", (doc_id,))
            conn.executemany(
                """
                INSERT INTO document_chunks(
                    chunk_id, doc_id, title, section_path, content, source, chunk_order, token_count
                )
                VALUES(?, ?, ?, ?, ?, ?, ?, ?)
                """,
                [
                    (
                        chunk.chunk_id,
                        chunk.doc_id,
                        chunk.title,
                        " / ".join(chunk.section_path),
                        chunk.content,
                        chunk.source,
                        chunk.order,
                        chunk.token_count,
                    )
                    for chunk in chunks
                ],
            )
            conn.commit()

    def list_documents(self) -> list[DocumentRecord]:
        with closing(self._connect()) as conn:
            rows = conn.execute(
                """
                SELECT id, title, source, path, file_size, chunk_count, created_at, updated_at
                FROM documents
                ORDER BY title
                """
            ).fetchall()
        return [
            DocumentRecord(
                id=row[0],
                title=row[1],
                source=row[2],
                path=row[3],
                file_size=row[4],
                chunk_count=row[5],
                created_at=row[6],
                updated_at=row[7],
            )
            for row in rows
        ]

    def list_chunks(self) -> list[DocumentChunk]:
        with closing(self._connect()) as conn:
            rows = conn.execute(
                """
                SELECT doc_id, chunk_id, title, section_path, content, source, chunk_order, token_count
                FROM document_chunks
                ORDER BY chunk_order
                """
            ).fetchall()
        return [
            DocumentChunk(
                doc_id=row[0],
                chunk_id=row[1],
                title=row[2],
                section_path=row[3].split(" / ") if row[3] else [],
                content=row[4],
                source=row[5],
                order=row[6],
                token_count=row[7],
            )
            for row in rows
        ]

    def ensure_chat_session(self, session_id: str, title: str = "") -> None:
        now = self._now()
        with closing(self._connect()) as conn:
            conn.execute(
                """
                INSERT INTO chat_sessions(session_id, title, created_at, updated_at)
                VALUES(?, ?, ?, ?)
                ON CONFLICT(session_id) DO UPDATE SET
                    updated_at = excluded.updated_at,
                    title = CASE
                        WHEN chat_sessions.title = '' THEN excluded.title
                        ELSE chat_sessions.title
                    END
                """,
                (session_id, title, now, now),
            )
            conn.commit()

    def save_chat_message(self, session_id: str, role: str, content: str) -> None:
        self.ensure_chat_session(session_id, title=content[:32] if role == "user" else "")
        with closing(self._connect()) as conn:
            conn.execute(
                """
                INSERT INTO chat_messages(id, session_id, role, content, created_at)
                VALUES(?, ?, ?, ?, ?)
                """,
                (uuid.uuid4().hex, session_id, role, content, self._now()),
            )
            conn.execute(
                "UPDATE chat_sessions SET updated_at = ? WHERE session_id = ?",
                (self._now(), session_id),
            )
            conn.commit()

    def list_chat_sessions(self) -> list[dict[str, str]]:
        with closing(self._connect()) as conn:
            rows = conn.execute(
                "SELECT session_id, title, created_at, updated_at FROM chat_sessions ORDER BY updated_at DESC"
            ).fetchall()
        return [
            {"session_id": row[0], "title": row[1], "created_at": row[2], "updated_at": row[3]}
            for row in rows
        ]

    def list_chat_messages(self, session_id: str) -> list[dict[str, str]]:
        with closing(self._connect()) as conn:
            rows = conn.execute(
                """
                SELECT role, content, created_at
                FROM chat_messages
                WHERE session_id = ?
                ORDER BY created_at ASC
                """,
                (session_id,),
            ).fetchall()
        return [{"role": row[0], "content": row[1], "created_at": row[2]} for row in rows]

    def save_tool_log(
        self,
        session_id: str,
        tool_name: str,
        input_payload: dict,
        output_payload: dict,
        status: str,
    ) -> None:
        self.ensure_chat_session(session_id)
        with closing(self._connect()) as conn:
            conn.execute(
                """
                INSERT INTO tool_logs(id, session_id, tool_name, input_json, output_json, status, created_at)
                VALUES(?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    uuid.uuid4().hex,
                    session_id,
                    tool_name,
                    json.dumps(input_payload, ensure_ascii=False),
                    json.dumps(output_payload, ensure_ascii=False),
                    status,
                    self._now(),
                ),
            )
            conn.commit()

    def list_tool_logs(self, session_id: str) -> list[dict[str, object]]:
        with closing(self._connect()) as conn:
            rows = conn.execute(
                """
                SELECT tool_name, input_json, output_json, status, created_at
                FROM tool_logs
                WHERE session_id = ?
                ORDER BY created_at ASC
                """,
                (session_id,),
            ).fetchall()
        return [
            {
                "tool_name": row[0],
                "input": json.loads(row[1]),
                "output": json.loads(row[2]),
                "status": row[3],
                "created_at": row[4],
            }
            for row in rows
        ]

    def _now(self) -> str:
        return datetime.now(timezone.utc).isoformat()
