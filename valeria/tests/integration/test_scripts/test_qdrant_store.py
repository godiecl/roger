"""
Smoke test del QdrantVectorStore contra un Qdrant en memoria.

No requiere docker ni un servidor Qdrant: usa el modo `:memory:` que
qdrant-client expone con el AsyncQdrantClient. Eso valida que la integración
con la API real funciona end-to-end (no solo que los imports compilan).

Si el test falla con "method not found" o similar, es un cambio en la API de
qdrant-client que rompe el adapter.
"""
from __future__ import annotations

import asyncio
import os
import sys
from pathlib import Path

import numpy as np
import pytest

VALERIA_DIR = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(VALERIA_DIR))

# Settings antes de importar nada que dependa de él.
os.environ.setdefault("SECRET_KEY", "test-qdrant-smoke")
os.environ.setdefault("LLM_PROVIDER", "groq")
os.environ.setdefault("GROQ_API_KEY", "test")
os.environ.setdefault("REDIS_ENABLED", "false")
# El adapter lee qdrant_url; pero como vamos a inyectar :memory: por monkey-patch,
# el valor de la setting no importa.
os.environ.setdefault("QDRANT_URL", "http://unused")


@pytest.fixture
def in_memory_store(monkeypatch):
    """
    QdrantVectorStore que internamente apunta a un AsyncQdrantClient :memory:.
    Reemplaza el __init__ tras instanciar para forzar el cliente in-memory.
    """
    from qdrant_client import AsyncQdrantClient
    from app.infrastructure.rag.vector_stores import qdrant_store

    # Construir manualmente sin pasar por __init__ (que apunta a URL).
    store = qdrant_store.QdrantVectorStore.__new__(qdrant_store.QdrantVectorStore)
    store.collection_name = "smoke_test"
    store.vector_size = 4
    store._distance = qdrant_store.qmodels.Distance.COSINE
    store.client = AsyncQdrantClient(":memory:")
    store._collection_ready = False
    return store


def _vec(*xs: float) -> np.ndarray:
    return np.array(xs, dtype=float)


async def _add_sample(store):
    await store.add_documents(
        documents=["hola", "mundo", "tercer documento"],
        embeddings=[_vec(1, 0, 0, 0), _vec(0, 1, 0, 0), _vec(0, 0, 1, 0)],
        metadatas=[{"k": "a", "year": 1940}, {"k": "b", "year": 1950}, {"k": "a", "year": 1960}],
        ids=["1", "2", "3"],
    )


@pytest.mark.asyncio
async def test_add_and_count(in_memory_store):
    await _add_sample(in_memory_store)
    assert await in_memory_store.count() == 3


@pytest.mark.asyncio
async def test_query_devuelve_shape_chroma(in_memory_store):
    await _add_sample(in_memory_store)
    res = await in_memory_store.query(_vec(1, 0, 0, 0), n_results=2)

    # Mismo shape que ChromaVectorStore
    assert set(res.keys()) == {"documents", "metadatas", "distances", "ids"}
    assert all(isinstance(v, list) and len(v) == 1 for v in res.values())

    # El primer hit debe ser "hola" (vector idéntico al de consulta)
    assert res["documents"][0][0] == "hola"
    assert res["ids"][0][0] == "1"
    # distance = 1 - score → con cosine identical = score 1 → distance ~0
    assert res["distances"][0][0] < 0.01


@pytest.mark.asyncio
async def test_filter_eq(in_memory_store):
    await _add_sample(in_memory_store)
    res = await in_memory_store.query(_vec(1, 0, 0, 0), n_results=10, where={"k": "a"})
    returned_ks = [m["k"] for m in res["metadatas"][0]]
    assert returned_ks == ["a", "a"]  # solo los dos con k=a


@pytest.mark.asyncio
async def test_filter_range(in_memory_store):
    await _add_sample(in_memory_store)
    res = await in_memory_store.query(
        _vec(0, 1, 0, 0), n_results=10, where={"year": {"$gte": 1945, "$lte": 1955}}
    )
    assert [m["year"] for m in res["metadatas"][0]] == [1950]


@pytest.mark.asyncio
async def test_get_y_delete(in_memory_store):
    await _add_sample(in_memory_store)
    got = await in_memory_store.get(["1", "3"])
    assert sorted(got["ids"]) == ["1", "3"]
    assert "hola" in got["documents"]

    await in_memory_store.delete(["1", "3"])
    assert await in_memory_store.count() == 1


@pytest.mark.asyncio
async def test_factory_resuelve_qdrant_cuando_setting_lo_dice(monkeypatch):
    """
    El factory debe instanciar QdrantVectorStore cuando VECTOR_STORE_PROVIDER=qdrant.
    Solo testeamos el switch (la conexión real va fallar contra http://unused,
    eso no nos importa aquí — importa que el TIPO sea correcto).
    """
    monkeypatch.setenv("VECTOR_STORE_PROVIDER", "qdrant")

    # Forzar reload de settings
    from app.config import settings as settings_module
    from importlib import reload
    reload(settings_module)

    from app.infrastructure.rag.vector_stores.vector_store_factory import VectorStoreFactory
    from app.infrastructure.rag.vector_stores.qdrant_store import QdrantVectorStore

    store = VectorStoreFactory.create(collection_name="test")
    assert isinstance(store, QdrantVectorStore)
