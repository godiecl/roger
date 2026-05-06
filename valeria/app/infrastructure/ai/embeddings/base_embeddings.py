"""
Base embeddings interface for ROGER - Valeria API
"""

from abc import ABC, abstractmethod
from typing import List
import numpy as np


class BaseEmbeddings(ABC):
    """Abstract base class for embedding implementations."""
    
    @abstractmethod
    async def embed_text(self, text: str) -> np.ndarray:
        """
        Generate embedding for a single text.
        
        Args:
            text: Input text
            
        Returns:
            Embedding vector as numpy array
        """
        pass
    
    @abstractmethod
    async def embed_texts(self, texts: List[str]) -> List[np.ndarray]:
        """
        Generate embeddings for multiple texts.
        
        Args:
            texts: List of input texts
            
        Returns:
            List of embedding vectors
        """
        pass
    
    @property
    @abstractmethod
    def dimension(self) -> int:
        """Get embedding dimension."""
        pass
