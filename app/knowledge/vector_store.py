from pathlib import Path

import chromadb
from chromadb import PersistentClient

from app.config import settings


class VectorStore:
    """ChromaDB wrapper for knowledge chunk embeddings."""

    def __init__(self, persist_dir: str | None = None):
        persist_dir = persist_dir or settings.chroma_db_path
        Path(persist_dir).mkdir(parents=True, exist_ok=True)
        self._client = PersistentClient(path=persist_dir)
        self._collection = self._client.get_or_create_collection(
            name="knowledge_chunks",
            metadata={"hnsw:space": "cosine"},
        )

    def add_chunk(self, chunk_id: str, embedding: list[float], metadata: dict, content: str):
        self._collection.add(
            ids=[chunk_id],
            embeddings=[embedding],
            metadatas=[metadata],
            documents=[content],
        )

    def add_chunks(self, ids: list[str], embeddings: list[list[float]], metadatas: list[dict], contents: list[str]):
        self._collection.add(
            ids=ids,
            embeddings=embeddings,
            metadatas=metadatas,
            documents=contents,
        )

    def semantic_search(self, query_embedding: list[float], top_k: int = 5, filter: dict | None = None) -> list[dict]:
        results = self._collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            where=filter,
        )
        return self._format_results(results)

    def delete_document_chunks(self, document_id: int):
        self._collection.delete(where={"document_id": document_id})

    def delete_all(self):
        self._client.delete_collection("knowledge_chunks")
        self._collection = self._client.get_or_create_collection(
            name="knowledge_chunks",
            metadata={"hnsw:space": "cosine"},
        )

    @staticmethod
    def _format_results(results) -> list[dict]:
        formatted = []
        if not results["ids"]:
            return formatted
        for i, chunk_id in enumerate(results["ids"][0]):
            formatted.append({
                "id": chunk_id,
                "content": results["documents"][0][i] if results.get("documents") else "",
                "metadata": results["metadatas"][0][i] if results.get("metadatas") else {},
                "distance": results["distances"][0][i] if results.get("distances") else 0.0,
            })
        return formatted
