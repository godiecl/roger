"""
Narrative generation workflow orchestrating multiple steps
"""

from typing import Dict, Any, List


class NarrativeWorkflow:
    """
    Multi-step workflow for narrative generation:
    1. Retrieve relevant context from RAG
    2. Generate narrative with LLM
    3. Extract sources and classify veracity
    4. Cache the result
    """
    
    def __init__(self, retriever, narrative_chain, cache):
        self.retriever = retriever
        self.narrative_chain = narrative_chain
        self.cache = cache
    
    async def execute(
        self,
        image_metadata: Dict[str, Any],
        query: str = ""
    ) -> Dict[str, Any]:
        """
        Execute the full narrative generation workflow.
        
        Args:
            image_metadata: Image metadata
            query: Optional user query
            
        Returns:
            Complete narrative with sources and metadata
        """
        # Step 1: Build retrieval query
        retrieval_query = self._build_retrieval_query(image_metadata, query)
        
        # Step 2: Retrieve relevant context
        retrieved_docs = await self.retriever.retrieve(
            query=retrieval_query,
            n_results=5
        )
        
        # Step 3: Format context for LLM
        context = self._format_context(retrieved_docs)
        
        # Step 4: Generate narrative
        narrative = await self.narrative_chain.generate(
            image_metadata=image_metadata,
            retrieved_context=context,
            query=query
        )
        
        # Step 5: Add retrieved sources
        narrative['retrieved_sources'] = [
            {
                'text': doc['text'][:200] + "...",
                'metadata': doc['metadata'],
                'score': doc['score']
            }
            for doc in retrieved_docs
        ]
        
        # Step 6: Cache result
        cache_key = f"narrative:{image_metadata.get('id')}"
        await self.cache.set(cache_key, narrative, ttl=3600)
        
        return narrative
    
    def _build_retrieval_query(
        self,
        image_metadata: Dict[str, Any],
        query: str
    ) -> str:
        """Build query for RAG retrieval."""
        parts = []
        
        if image_metadata.get('title'):
            parts.append(f"Imagen: {image_metadata['title']}")
        if image_metadata.get('year'):
            parts.append(f"Año: {image_metadata['year']}")
        if image_metadata.get('location'):
            parts.append(f"Ubicación: {image_metadata['location']}")
        if query:
            parts.append(query)
        
        return " ".join(parts)
    
    def _format_context(self, documents: List[Dict[str, Any]]) -> str:
        """Format retrieved documents as context."""
        context_parts = []
        
        for i, doc in enumerate(documents, 1):
            metadata = doc['metadata']
            source_type = metadata.get('type', 'verosimil').upper()
            source = metadata.get('source', 'Unknown')
            
            context_parts.append(f"""
[FUENTE {i}] - [{source_type}]
Origen: {source}
Año: {metadata.get('year', 'N/A')}
Texto: {doc['text']}
---
""")
        
        return "\n".join(context_parts)
