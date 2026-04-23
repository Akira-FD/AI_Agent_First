import unittest

from app.rag.factory import build_retriever
from app.rag.retriever import Retriever


class RetrievalFactoryTests(unittest.TestCase):
    def test_builds_local_retriever_with_in_memory_store_and_hash_embedding(self) -> None:
        class Settings:
            retrieval_top_k = 5
            retrieval_backend = "in-memory"
            embedding_backend = "hash"
            reranker_backend = "keyword"
            bge_reranker_model = "BAAI/bge-reranker-v2-m3"
            milvus_enabled = False
            milvus_uri = "http://localhost:19530"
            milvus_collection = "ai_agent_first_chunks"
            milvus_dimension = 64
            milvus_lite_path = "data/milvus/agent.db"
            remote_retrieval_url = ""

        retriever = build_retriever(settings=Settings(), repository=object())

        self.assertIsInstance(retriever, Retriever)
        self.assertEqual(retriever.vector_store.__class__.__name__, "InMemoryVectorStore")
        self.assertEqual(retriever.embedding_provider.__class__.__name__, "HashEmbeddingProvider")
        self.assertEqual(retriever.reranker.__class__.__name__, "KeywordReranker")

    def test_builds_remote_retriever_with_remote_vector_store(self) -> None:
        class Settings:
            retrieval_top_k = 5
            retrieval_backend = "remote"
            embedding_backend = "hash"
            reranker_backend = "keyword"
            bge_reranker_model = "BAAI/bge-reranker-v2-m3"
            milvus_enabled = False
            milvus_uri = "http://localhost:19530"
            milvus_collection = "ai_agent_first_chunks"
            milvus_dimension = 64
            milvus_lite_path = "data/milvus/agent.db"
            remote_retrieval_url = "http://127.0.0.1:9000/retrieve"

        retriever = build_retriever(settings=Settings(), repository=object())

        self.assertEqual(retriever.vector_store.__class__.__name__, "RemoteVectorStore")
        self.assertEqual(retriever.vector_store.endpoint_url, "http://127.0.0.1:9000/retrieve")

    def test_builds_milvus_lite_retriever_with_bge_reranker(self) -> None:
        class Settings:
            retrieval_top_k = 5
            retrieval_backend = "milvus-lite"
            embedding_backend = "hash"
            reranker_backend = "bge"
            bge_reranker_model = "BAAI/bge-reranker-v2-m3"
            milvus_enabled = False
            milvus_uri = "http://localhost:19530"
            milvus_collection = "ai_agent_first_chunks"
            milvus_dimension = 64
            milvus_lite_path = "data/milvus/agent.db"
            remote_retrieval_url = ""

        retriever = build_retriever(
            settings=Settings(),
            repository=object(),
            client=object(),
            reranker_scorer=lambda pairs: [0.5 for _ in pairs],
        )

        self.assertEqual(retriever.vector_store.backend_name(), "milvus-lite")
        self.assertEqual(retriever.reranker.backend_name(), "bge")


if __name__ == "__main__":
    unittest.main()
