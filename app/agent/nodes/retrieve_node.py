from __future__ import annotations

from app.rag.retriever import Retriever


def run_retrieval(query: str, retriever: Retriever):
    return retriever.retrieve(query)
