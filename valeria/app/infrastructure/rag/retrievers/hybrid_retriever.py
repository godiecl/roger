"""
Hybrid retriever (dense + sparse) for ROGER - Valeria API
"""

from typing import List, Dict, Any
from rank_bm25 import BM25Okapi

from app.infrastructure.rag.retrievers.base_retriever import BaseRetriever
from app.infrastructure.rag.vector_stores.base_vector_store import BaseVectorStore
from app.infrastructure.ai.embeddings.base_embeddings import BaseEmbeddings


class HybridRetriever(BaseRetriever):
    """
    Hybrid retrieval combining dense (semantic) and sparse (BM25) retrieval.
    """
    
    def __init__(
        self,
        vector_store: BaseVectorStore,
        embeddings: BaseEmbeddings,
        dense_weight: float = 0.7,
        sparse_weight: float = 0.3
    ):
        self.vector_store = vector_store
        self.embeddings = embeddings
        self.dense_weight = dense_weight
        self.sparse_weight = sparse_weight
        
        # BM25 will be initialized with corpus
        self.bm25 = None
        self.corpus = []
        self.corpus_ids = []
    
    async def index_corpus(self, documents: List[Dict[str, Any]]) -> None:
        """
        Index corpus for BM25 sparse retrieval.
        
        Args:
            documents: List of dicts with 'id' and 'text' keys
        """
        self.corpus = [doc['text'] for doc in documents]
        self.corpus_ids = [doc['id'] for doc in documents]
        
        # Tokenize and create BM25 index
        tokenized_corpus = [doc.split() for doc in self.corpus]
        self.bm25 = BM25Okapi(tokenized_corpus)
    
    async def retrieve(
        self,
        query: str,
        n_results: int = 10,
        filters: Dict[str, Any] = None
    ) -> List[Dict[str, Any]]:
        """Retrieve documents using hybrid dense + sparse approach."""
        # 1. DENSE RETRIEVAL (semantic)
        query_embedding = await self.embeddings.embed_text(query)
        
        dense_results = await self.vector_store.query(
            query_embedding=query_embedding,
            n_results=n_results * 2,  # Get more for reranking
            where=filters
        )
        
        # 2. SPARSE RETRIEVAL (BM25)
        sparse_scores = {}
        if self.bm25 is not None:
            tokenized_query = query.split()
            bm25_scores = self.bm25.get_scores(tokenized_query)
            
            # Normalize BM25 scores
            max_score = max(bm25_scores) if len(bm25_scores) > 0 else 1.0
            for doc_id, score in zip(self.corpus_ids, bm25_scores):
                sparse_scores[doc_id] = score / (max_score + 1e-6)
        
        # 3. COMBINE SCORES
        combined_results = []
        
        for i, doc_id in enumerate(dense_results['ids']):
            # Dense score (convert distance to similarity)
            dense_score = 1 / (1 + dense_results['distances'][i])
            
            # Sparse score (BM25)
            sparse_score = sparse_scores.get(doc_id, 0.0)
            
            # Combined score
            combined_score = (
                self.dense_weight * dense_score +
                self.sparse_weight * sparse_score
            )
            
            combined_results.append({
                'id': doc_id,
                'text': dense_results['documents'][i],
                'metadata': dense_results['metadatas'][i],
                'score': combined_score,
                'dense_score': dense_score,
                'sparse_score': sparse_score
            })
        
        # 4. SORT by combined score
        combined_results.sort(key=lambda x: x['score'], reverse=True)
        
        return combined_results[:n_results]
