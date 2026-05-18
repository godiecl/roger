"""
Sentence Transformers embeddings — no API key required.
Model: paraphrase-multilingual-MiniLM-L12-v2 (384-dim, multilingual)
"""

import asyncio
from typing import List
from functools import partial

import numpy as np
from sentence_transformers import SentenceTransformer

from app.infrastructure.ai.embeddings.base_embeddings import BaseEmbeddings

_MODEL_NAME = "paraphrase-multilingual-MiniLM-L12-v2"


class SentenceTransformerEmbeddings(BaseEmbeddings):
    """Local sentence-transformers embeddings. Sync encode run in executor."""

    def __init__(self, model_name: str = _MODEL_NAME):
        self._model = SentenceTransformer(model_name)
        self._dimension = self._model.get_sentence_embedding_dimension()

    def _encode(self, texts: List[str]) -> np.ndarray:
        return self._model.encode(texts, convert_to_numpy=True, normalize_embeddings=True)

    async def embed_text(self, text: str) -> np.ndarray:
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(None, partial(self._encode, [text]))
        return result[0].astype(np.float32)

    async def embed_texts(self, texts: List[str]) -> List[np.ndarray]:
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(None, partial(self._encode, texts))
        return [row.astype(np.float32) for row in result]

    @property
    def dimension(self) -> int:
        return self._dimension


# Global instance
sentence_transformer_embeddings = SentenceTransformerEmbeddings()
