from __future__ import annotations

import sqlite3
from contextlib import closing
from pathlib import Path

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
                    path TEXT
                )
                """
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
            conn.commit()

    def upsert_document(self, document: DocumentRecord) -> None:
        with closing(self._connect()) as conn:
            conn.execute(
                """
                INSERT INTO documents(id, title, source, path)
                VALUES(?, ?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                    title = excluded.title,
                    source = excluded.source,
                    path = excluded.path
                """,
                (document.id, document.title, document.source, document.path),
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
            rows = conn.execute("SELECT id, title, source, path FROM documents ORDER BY title").fetchall()
        return [DocumentRecord(id=row[0], title=row[1], source=row[2], path=row[3]) for row in rows]

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
