"""
Dense retriever (semantic search with embeddings) for ROGER - Valeria API
"""

from typing import List, Dict, Any

from app.infrastructure.rag.retrievers.base_retriever import BaseRetriever
from app.infrastructure.rag.vector_stores.base_vector_store import BaseVectorStore
from app.infrastructure.ai.embeddings.base_embeddings import BaseEmbeddings


class DenseRetriever(BaseRetriever):
    """Dense retrieval using semantic embeddings."""
    
    def __init__(
        self,
        vector_store: BaseVectorStore,
        embeddings: BaseEmbeddings
    ):
        self.vector_store = vector_store
        self.embeddings = embeddings
    
    async def retrieve(
        self,
        query: str,
        n_results: int = 10,
        filters: Dict[str, Any] = None
    ) -> List[Dict[str, Any]]:
        """Retrieve documents using dense embeddings."""
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
                'score': 1 / (1 + results['distances'][i]),  # Convert distance to score
                'distance': results['distances'][i]
            })
        
        return documents
