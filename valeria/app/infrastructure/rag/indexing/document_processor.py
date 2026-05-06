"""
Document processor for indexing in RAG pipeline
"""

from typing import List, Dict, Any
import uuid


class DocumentProcessor:
    """
    Process documents for indexing in vector store.
    Handles chunking, metadata extraction, and preparation.
    """
    
    def __init__(self, chunk_size: int = 512, chunk_overlap: int = 50):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
    
    def process_document(self, document: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Process a document into chunks ready for indexing.
        
        Args:
            document: Dict with 'text' and optional 'metadata'
            
        Returns:
            List of processed chunks with IDs, text, and metadata
        """
        text = document['text']
        metadata = document.get('metadata', {})
        
        # Chunk the text
        chunks = self._chunk_text(text)
        
        # Create processed chunks
        processed = []
        for i, chunk in enumerate(chunks):
            chunk_id = f"{document.get('id', str(uuid.uuid4()))}_chunk_{i}"
            
            processed.append({
                'id': chunk_id,
                'text': chunk,
                'metadata': {
                    **metadata,
                    'chunk_index': i,
                    'total_chunks': len(chunks)
                }
            })
        
        return processed
    
    def _chunk_text(self, text: str) -> List[str]:
        """
        Split text into chunks with overlap.
        
        Uses simple sentence-based chunking.
        In production, you might want more sophisticated methods.
        """
        # Split by paragraphs first
        paragraphs = text.split('\n\n')
        
        chunks = []
        current_chunk = ""
        
        for para in paragraphs:
            # If adding this paragraph exceeds chunk size, save current chunk
            if len(current_chunk) + len(para) > self.chunk_size and current_chunk:
                chunks.append(current_chunk.strip())
                # Keep overlap
                current_chunk = current_chunk[-self.chunk_overlap:] if len(current_chunk) > self.chunk_overlap else ""
            
            current_chunk += para + "\n\n"
        
        # Add final chunk
        if current_chunk.strip():
            chunks.append(current_chunk.strip())
        
        return chunks if chunks else [text]  # Return original if no chunks created
    
    def extract_metadata(self, document: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract and enrich metadata from document.
        
        Args:
            document: Document dict
            
        Returns:
            Enriched metadata
        """
        metadata = document.get('metadata', {})
        
        # Extract year if present in text
        # Extract entities if needed
        # etc.
        
        return metadata


# Global instance
document_processor = DocumentProcessor()
