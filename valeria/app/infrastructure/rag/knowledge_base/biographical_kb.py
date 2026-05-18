"""
Biographical knowledge base — Gerstmann timeline entries.
Source: gerstmann_timeline.json (22 biographical periods)
"""

from typing import List, Dict, Any
import uuid

from app.infrastructure.rag.knowledge_base.base_kb import BaseKnowledgeBase
from app.infrastructure.rag.vector_stores.chroma_store import ChromaVectorStore
from app.infrastructure.ai.embeddings.sentence_transformer_embeddings import sentence_transformer_embeddings


class BiographicalKnowledgeBase(BaseKnowledgeBase):
    """Knowledge base for Gerstmann biographical timeline."""

    def __init__(self):
        self.vector_store = ChromaVectorStore("biographical_docs")
        self.embeddings = sentence_transformer_embeddings

    async def add_document(self, document: Dict[str, Any]) -> str:
        doc_id = document.get("id", str(uuid.uuid4()))
        text = document["text"]
        metadata = document.get("metadata", {})

        embedding = await self.embeddings.embed_text(text)
        await self.vector_store.add_documents(
            documents=[text],
            embeddings=[embedding],
            metadatas=[metadata],
            ids=[doc_id],
        )
        return doc_id

    async def search(
        self,
        query: str,
        n_results: int = 5,
        filters: Dict[str, Any] = None,
    ) -> List[Dict[str, Any]]:
        """Search biographical periods by semantic similarity."""
        query_embedding = await self.embeddings.embed_text(query)
        results = await self.vector_store.query(
            query_embedding=query_embedding,
            n_results=n_results,
            where=filters,
        )
        return [
            {
                "id": doc_id,
                "text": results["documents"][i],
                "metadata": results["metadatas"][i],
                "score": 1 / (1 + results["distances"][i]),
            }
            for i, doc_id in enumerate(results["ids"])
        ]

    async def get_by_id(self, doc_id: str) -> Dict[str, Any]:
        results = await self.vector_store.get([doc_id])
        if not results["ids"]:
            return None
        return {
            "id": results["ids"][0],
            "text": results["documents"][0],
            "metadata": results["metadatas"][0],
        }

    async def delete(self, doc_id: str) -> bool:
        await self.vector_store.delete([doc_id])
        return True


# Global instance
biographical_kb = BiographicalKnowledgeBase()
