import unittest

from app.models.document import DocumentChunk
from app.rag.embedding_service import HashEmbeddingService
from app.rag.vector_store import MilvusVectorStore, build_vector_store


class FakeMilvusClient:
    def __init__(self) -> None:
        self.collections: dict[str, list[dict]] = {}
        self.created = []
        self.inserted = []
        self.search_requests = []

    def has_collection(self, collection_name: str) -> bool:
        return collection_name in self.collections

    def create_collection(self, collection_name: str, dimension: int, metric_type: str = "COSINE") -> None:
        self.created.append((collection_name, dimension, metric_type))
        self.collections[collection_name] = []

    def upsert(self, collection_name: str, data: list[dict]) -> None:
        self.inserted.extend(data)
        by_id = {item["chunk_id"]: item for item in self.collections[collection_name]}
        for item in data:
            by_id[item["chunk_id"]] = item
        self.collections[collection_name] = list(by_id.values())

    def search(
        self,
        collection_name: str,
        data: list[list[float]],
        limit: int,
        output_fields: list[str],
        search_params: dict,
    ):
        self.search_requests.append(
            {
                "collection_name": collection_name,
                "data": data,
                "limit": limit,
                "output_fields": output_fields,
                "search_params": search_params,
            }
        )
        rows = self.collections[collection_name][:limit]
        return [
            [
                {
                    "distance": 0.9 - index * 0.1,
                    "entity": {field: row[field] for field in output_fields},
                }
                for index, row in enumerate(rows)
            ]
        ]


class MilvusVectorStoreTests(unittest.TestCase):
    def test_hash_embedding_returns_fixed_dimension_dense_vector(self) -> None:
        vector = HashEmbeddingService(dimension=8).embed_dense("redis maxmemory slowlog")

        self.assertEqual(len(vector), 8)
        self.assertTrue(all(isinstance(value, float) for value in vector))
        self.assertGreater(sum(abs(value) for value in vector), 0.0)

    def test_milvus_vector_store_upserts_chunks_and_searches_metadata(self) -> None:
        client = FakeMilvusClient()
        chunk = DocumentChunk(
            doc_id="doc-1",
            chunk_id="chunk-1",
            title="Redis OOM",
            section_path=["Redis", "OOM"],
            content="检查 maxmemory 和 slowlog。",
            source="redis.md",
            order=1,
            token_count=8,
        )
        store = MilvusVectorStore(
            client=client,
            collection_name="ai_agent_first_chunks",
            embedding_service=HashEmbeddingService(dimension=12),
            dimension=12,
        )

        indexed_count = store.upsert_chunks([chunk])
        matches = store.search("Redis OOM 怎么排查", chunks=[chunk], top_k=1)

        self.assertEqual(indexed_count, 1)
        self.assertEqual(client.created, [("ai_agent_first_chunks", 12, "COSINE")])
        self.assertEqual(client.inserted[0]["chunk_id"], "chunk-1")
        self.assertEqual(len(client.inserted[0]["vector"]), 12)
        self.assertEqual(matches[0].chunk.chunk_id, "chunk-1")
        self.assertGreater(matches[0].score, 0)

    def test_build_vector_store_falls_back_to_memory_when_milvus_is_disabled(self) -> None:
        class Settings:
            milvus_enabled = False
            retrieval_backend = "in-memory"
            milvus_uri = "http://localhost:19530"
            milvus_collection = "ai_agent_first_chunks"
            milvus_dimension = 32
            milvus_lite_path = "data/milvus/agent.db"

        store = build_vector_store(Settings())

        self.assertEqual(store.__class__.__name__, "InMemoryVectorStore")

    def test_build_vector_store_uses_milvus_lite_local_path(self) -> None:
        class Settings:
            retrieval_backend = "milvus-lite"
            milvus_enabled = False
            milvus_uri = "http://localhost:19530"
            milvus_collection = "ai_agent_first_chunks"
            milvus_dimension = 12
            milvus_lite_path = "data/milvus/agent.db"

        client = FakeMilvusClient()

        store = build_vector_store(Settings(), client=client)

        self.assertEqual(store.__class__.__name__, "MilvusVectorStore")
        self.assertEqual(store.backend_name(), "milvus-lite")


if __name__ == "__main__":
    unittest.main()
