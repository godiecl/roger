"""
Image knowledge base for ROGER - Valeria API
Stores image metadata and enables semantic search
"""

from typing import List, Dict, Any
import uuid

from app.infrastructure.rag.knowledge_base.base_kb import BaseKnowledgeBase
from app.infrastructure.rag.vector_stores.chroma_store import ChromaVectorStore
from app.infrastructure.ai.embeddings.openai_embeddings import openai_embeddings


class ImageKnowledgeBase(BaseKnowledgeBase):
    """Knowledge base for image metadata."""
    
    def __init__(self):
        self.vector_store = ChromaVectorStore("images")
        self.embeddings = openai_embeddings
    
    async def add_document(self, document: Dict[str, Any]) -> str:
        """
        Add an image document to the KB.
        
        Args:
            document: Dict with 'text' (description) and 'metadata' (image info)
        """
        doc_id = document.get('id', str(uuid.uuid4()))
        text = document['text']
        metadata = document.get('metadata', {})
        
        # Generate embedding
        embedding = await self.embeddings.embed_text(text)
        
        # Add to vector store
        await self.vector_store.add_documents(
            documents=[text],
            embeddings=[embedding],
            metadatas=[metadata],
            ids=[doc_id]
        )
        
        return doc_id
    
    async def search(
        self,
        query: str,
        n_results: int = 5,
        filters: Dict[str, Any] = None
    ) -> List[Dict[str, Any]]:
        """Search images by semantic similarity."""
        # Generate query embedding
        query_embedding = await self.embeddings.embed_text(query)
        
        # Search in vector store
        results = await self.vector_store.query(
            query_embedding=query_embedding,
            n_results=n_results,
            where=filters
        )
        
        # Format results
        documents = []
        for i, doc_id in enumerate(results['ids']):
            documents.append({
                'id': doc_id,
                'text': results['documents'][i],
                'metadata': results['metadatas'][i],
                'score': 1 / (1 + results['distances'][i])
            })
        
        return documents
    
    async def get_by_id(self, doc_id: str) -> Dict[str, Any]:
        """Get image document by ID."""
        results = await self.vector_store.get([doc_id])
        
        if not results['ids']:
            return None
        
        return {
            'id': results['ids'][0],
            'text': results['documents'][0],
            'metadata': results['metadatas'][0]
        }
    
    async def delete(self, doc_id: str) -> bool:
        """Delete image document."""
        await self.vector_store.delete([doc_id])
        return True


# Global instance
image_kb = ImageKnowledgeBase()
