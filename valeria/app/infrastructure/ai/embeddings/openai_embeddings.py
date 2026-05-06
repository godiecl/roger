"""
OpenAI embeddings implementation for ROGER - Valeria API
"""

from typing import List
import numpy as np
from openai import AsyncOpenAI

from app.infrastructure.ai.embeddings.base_embeddings import BaseEmbeddings
from app.config.settings import settings


class OpenAIEmbeddings(BaseEmbeddings):
    """OpenAI embeddings implementation."""
    
    def __init__(self):
        self.client = AsyncOpenAI(api_key=settings.openai_api_key)
        self.model = settings.openai_embedding_model
        self._dimension = 1536 if "small" in self.model else 3072
    
    async def embed_text(self, text: str) -> np.ndarray:
        """Generate embedding for a single text."""
        response = await self.client.embeddings.create(
            model=self.model,
            input=text
        )
        
        embedding = response.data[0].embedding
        return np.array(embedding, dtype=np.float32)
    
    async def embed_texts(self, texts: List[str]) -> List[np.ndarray]:
        """Generate embeddings for multiple texts."""
        response = await self.client.embeddings.create(
            model=self.model,
            input=texts
        )
        
        embeddings = [
            np.array(item.embedding, dtype=np.float32)
            for item in response.data
        ]
        return embeddings
    
    @property
    def dimension(self) -> int:
        """Get embedding dimension."""
        return self._dimension


# Global OpenAI embeddings instance
openai_embeddings = OpenAIEmbeddings()
