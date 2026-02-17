import chromadb
from chromadb.config import Settings as ChromaSettings

from config import settings


class VectorStore:
    def __init__(self, persist_dir: str = None):
        persist_dir = persist_dir or settings.chroma_persist_dir
        self.client = chromadb.PersistentClient(
            path=persist_dir,
            settings=ChromaSettings(anonymized_telemetry=False),
        )
        self.collection = self.client.get_or_create_collection(
            name="nakai_store_data",
            metadata={"hnsw:space": "cosine"},
        )

    def add_documents(
        self, documents: list[dict], embeddings: list[list[float]]
    ) -> None:
        """Add documents with pre-computed embeddings."""
        if not documents:
            return
        existing = self.collection.count()
        ids = [f"doc_{existing + i}" for i in range(len(documents))]
        self.collection.add(
            ids=ids,
            embeddings=embeddings,
            documents=[doc["text"] for doc in documents],
            metadatas=[doc["metadata"] for doc in documents],
        )

    def query(
        self, query_embedding: list[float], n_results: int = 5
    ) -> list[dict]:
        """Query similar documents by embedding."""
        count = self.collection.count()
        if count == 0:
            return []
        n = min(n_results, count)
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=n,
            include=["documents", "metadatas", "distances"],
        )
        return [
            {"text": doc, "metadata": meta, "distance": dist}
            for doc, meta, dist in zip(
                results["documents"][0],
                results["metadatas"][0],
                results["distances"][0],
            )
        ]

    def clear(self) -> None:
        """Clear all documents for re-ingestion."""
        self.client.delete_collection("nakai_store_data")
        self.collection = self.client.get_or_create_collection(
            name="nakai_store_data",
            metadata={"hnsw:space": "cosine"},
        )

    def count(self) -> int:
        return self.collection.count()
