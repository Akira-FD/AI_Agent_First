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
        self.collection_schemas: dict[str, dict] = {}
        self.collection_stats: dict[str, dict] = {}
        self.dropped = []
        self.flushed = []
        self.loaded = []

    def has_collection(self, collection_name: str) -> bool:
        return collection_name in self.collections

    def create_collection(
        self,
        collection_name: str,
        dimension: int,
        primary_field_name: str = "id",
        id_type: str = "int",
        vector_field_name: str = "vector",
        metric_type: str = "COSINE",
        auto_id: bool = False,
        max_length: int | None = None,
    ) -> None:
        self.created.append(
            {
                "collection_name": collection_name,
                "dimension": dimension,
                "primary_field_name": primary_field_name,
                "id_type": id_type,
                "vector_field_name": vector_field_name,
                "metric_type": metric_type,
                "auto_id": auto_id,
                "max_length": max_length,
            }
        )
        self.collections[collection_name] = []
        self.collection_schemas[collection_name] = {
            "collection_name": collection_name,
            "auto_id": auto_id,
            "fields": [
                {
                    "name": primary_field_name,
                    "type": id_type,
                    "is_primary": True,
                    "params": {"max_length": max_length} if max_length is not None else {},
                },
                {
                    "name": vector_field_name,
                    "type": "float_vector",
                    "is_primary": False,
                },
            ],
        }
        self.collection_stats[collection_name] = {"row_count": 0}

    def describe_collection(self, collection_name: str) -> dict:
        return self.collection_schemas[collection_name]

    def get_collection_stats(self, collection_name: str) -> dict:
        return self.collection_stats.get(collection_name, {"row_count": len(self.collections.get(collection_name, []))})

    def drop_collection(self, collection_name: str) -> None:
        self.dropped.append(collection_name)
        self.collections.pop(collection_name, None)
        self.collection_schemas.pop(collection_name, None)
        self.collection_stats.pop(collection_name, None)

    def flush(self, collection_name: str) -> None:
        self.flushed.append(collection_name)
        self.collection_stats[collection_name] = {"row_count": len(self.collections.get(collection_name, []))}

    def load_collection(self, collection_name: str) -> None:
        self.loaded.append(collection_name)

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
        self.assertEqual(
            client.created,
            [
                {
                    "collection_name": "ai_agent_first_chunks",
                    "dimension": 12,
                    "primary_field_name": "chunk_id",
                    "id_type": "string",
                    "vector_field_name": "vector",
                    "metric_type": "COSINE",
                    "auto_id": False,
                    "max_length": 512,
                }
            ],
        )
        self.assertEqual(client.inserted[0]["chunk_id"], "chunk-1")
        self.assertEqual(len(client.inserted[0]["vector"]), 12)
        self.assertEqual(client.loaded, ["ai_agent_first_chunks"])
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

    def test_milvus_vector_store_recreates_incompatible_empty_collection(self) -> None:
        client = FakeMilvusClient()
        client.collections["ai_agent_first_chunks"] = []
        client.collection_schemas["ai_agent_first_chunks"] = {
            "collection_name": "ai_agent_first_chunks",
            "auto_id": False,
            "fields": [
                {"name": "id", "type": "int", "is_primary": True},
                {"name": "vector", "type": "float_vector", "is_primary": False},
            ],
        }
        client.collection_stats["ai_agent_first_chunks"] = {"row_count": 0}

        MilvusVectorStore(
            client=client,
            collection_name="ai_agent_first_chunks",
            embedding_service=HashEmbeddingService(dimension=12),
            dimension=12,
        )

        self.assertEqual(client.dropped, ["ai_agent_first_chunks"])
        self.assertEqual(client.created[0]["primary_field_name"], "chunk_id")
        self.assertEqual(client.created[0]["id_type"], "string")
        self.assertEqual(client.created[0]["max_length"], 512)

    def test_milvus_vector_store_finalizes_ingest_with_single_flush_and_load(self) -> None:
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

        store.upsert_chunks([chunk])
        store.finalize_ingest()

        self.assertEqual(client.flushed, ["ai_agent_first_chunks"])
        self.assertEqual(client.loaded, ["ai_agent_first_chunks"])


if __name__ == "__main__":
    unittest.main()
