"""
Script to index all Gerstmann RAG data into the knowledge bases.

Sources (valeria/data/):
  gerstmann_timeline.json      -> biographical_kb  (22 biographical periods)
  gerstmann_descriptores.json  -> historical_kb    (visual descriptors)
  gerstmann_inventario_ucn.json -> image_kb        (physical archive inventory)

Usage:
  cd valeria
  python scripts/index_gerstmann.py
"""

import asyncio
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.infrastructure.rag.knowledge_base.biographical_kb import biographical_kb
from app.infrastructure.rag.knowledge_base.historical_kb import historical_kb
from app.infrastructure.rag.knowledge_base.image_kb import image_kb

DATA_DIR = Path(__file__).parent.parent / "data"


# ---------------------------------------------------------------------------
# Transformers — each converts raw JSON entries into {id, text, metadata}
# ---------------------------------------------------------------------------

def _timeline_to_doc(entry: dict) -> dict:
    """Convert a gerstmann_timeline.json entry to a biographical_kb document."""
    fecha_inicio = entry.get("fecha_inicio") or "?"
    fecha_fin = entry.get("fecha_fin") or "?"
    periodo = f"{fecha_inicio}–{fecha_fin}" if fecha_inicio != fecha_fin else str(fecha_inicio)

    parts = [f"{entry['titulo']} ({periodo})."]
    if entry.get("actividad"):
        parts.append(entry["actividad"])
    if entry.get("lugares"):
        parts.append(f"Lugares: {', '.join(entry['lugares'])}.")
    if entry.get("paises"):
        parts.append(f"Países: {', '.join(entry['paises'])}.")
    if entry.get("series"):
        titles = [s["titulo"] for s in entry["series"] if s.get("titulo")]
        if titles:
            parts.append(f"Series fotográficas: {', '.join(titles)}.")
    if entry.get("publicaciones"):
        pubs = [p["titulo"] for p in entry["publicaciones"] if p.get("titulo")]
        if pubs:
            parts.append(f"Publicaciones: {', '.join(pubs)}.")
    if entry.get("notas"):
        parts.append(f"Notas: {entry['notas']}")

    return {
        "id": f"bio_{entry['id']}",
        "text": " ".join(parts),
        "metadata": {
            "source": "gerstmann_timeline",
            "type": entry.get("tipo", ""),
            "fecha_inicio": str(fecha_inicio),
            "fecha_fin": str(fecha_fin),
            "paises": ", ".join(entry.get("paises") or []),
            "lugares": ", ".join(entry.get("lugares") or []),
            "confianza": str(entry.get("confianza", "")),
            "fuentes": ", ".join(entry.get("fuentes") or []),
            "source_type": "veraz",
        },
    }


def _descriptor_to_doc(entry: dict, index: int) -> dict:
    """Convert a gerstmann_descriptores.json descriptor to a historical_kb document."""
    text = entry["descriptor"]
    if entry.get("notas"):
        text += f" Notas: {entry['notas']}"

    return {
        "id": f"hist_{index:03d}",
        "text": text,
        "metadata": {
            "source": "gerstmann_descriptores",
            "paises_probables": ", ".join(entry.get("paises_probables") or []),
            "periodos_probables": ", ".join(entry.get("periodos_probables") or []),
            "anos_probables": str(entry.get("años_probables", "")),
            "lugares": ", ".join(entry.get("lugares") or []),
            "ids_ucn": ", ".join(str(i) for i in (entry.get("ids_ucn_relevantes") or [])),
            "source_type": "verosimil",
        },
    }


def _inventario_to_doc(item: dict) -> dict:
    """Convert a gerstmann_inventario_ucn.json item to an image_kb document."""
    parts = [
        f"UCN cajón {item['cajon']}, ítem {item['id']}: {item['titulo']}.",
        f"Tipo: {item['tipo']}.",
        f"Soporte: {item.get('soporte', '')}.",
        f"Negativos: {item['neg']}, Positivos: {item['pos']}.",
    ]
    if item.get("tags"):
        parts.append(f"Tags: {', '.join(item['tags'])}.")
    if item.get("estado"):
        parts.append(f"Estado: {item['estado']}.")

    return {
        "id": f"ucn_{item['cajon']}_{item['id']}",
        "text": " ".join(parts),
        "metadata": {
            "source": "inventario_ucn",
            "cajon": str(item["cajon"]),
            "item_id": str(item["id"]),
            "tipo": item.get("tipo", ""),
            "titulo": item.get("titulo", ""),
            "color": item.get("color", ""),
            "soporte": item.get("soporte", ""),
            "neg": str(item.get("neg", 0)),
            "pos": str(item.get("pos", 0)),
            "source_type": "veraz",
        },
    }


# ---------------------------------------------------------------------------
# Indexing functions
# ---------------------------------------------------------------------------

async def index_biographical():
    path = DATA_DIR / "gerstmann_timeline.json"
    entries = json.loads(path.read_text(encoding="utf-8"))
    print(f"\n[biographical_kb] Indexing {len(entries)} timeline entries...")
    ok = 0
    for entry in entries:
        try:
            doc = _timeline_to_doc(entry)
            await biographical_kb.add_document(doc)
            print(f"  + {doc['id']}: {entry['titulo'][:60]}")
            ok += 1
        except Exception as e:
            print(f"  ! ERROR {entry.get('id')}: {e}")
    print(f"  => {ok}/{len(entries)} indexed")


async def index_historical():
    path = DATA_DIR / "gerstmann_descriptores.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    descriptors = data.get("descriptores_clip", [])
    print(f"\n[historical_kb] Indexing {len(descriptors)} visual descriptors...")
    ok = 0
    for i, entry in enumerate(descriptors):
        try:
            doc = _descriptor_to_doc(entry, i)
            await historical_kb.add_document(doc)
            print(f"  + {doc['id']}: {entry['descriptor'][:60]}")
            ok += 1
        except Exception as e:
            print(f"  ! ERROR descriptor_{i}: {e}")
    print(f"  => {ok}/{len(descriptors)} indexed")


async def index_inventario():
    path = DATA_DIR / "gerstmann_inventario_ucn.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    items = data.get("items", [])
    print(f"\n[image_kb] Indexing {len(items)} UCN inventory items...")
    ok = 0
    for item in items:
        try:
            doc = _inventario_to_doc(item)
            await image_kb.add_document(doc)
            ok += 1
        except Exception as e:
            print(f"  ! ERROR ucn_{item.get('cajon')}_{item.get('id')}: {e}")
    print(f"  => {ok}/{len(items)} indexed")


async def test_search():
    print("\n[test] Searching each KB...")

    r = await biographical_kb.search("expedición antártica", n_results=2)
    print(f"\n  biographical_kb 'expedición antártica': {len(r)} result(s)")
    for doc in r:
        print(f"    score={doc['score']:.3f} | {doc['text'][:80]}")

    r = await historical_kb.search("mina de estaño Bolivia", n_results=2)
    print(f"\n  historical_kb 'mina de estaño Bolivia': {len(r)} result(s)")
    for doc in r:
        print(f"    score={doc['score']:.3f} | {doc['text'][:80]}")

    r = await image_kb.search("Sacambaya negativos", n_results=2)
    print(f"\n  image_kb 'Sacambaya negativos': {len(r)} result(s)")
    for doc in r:
        print(f"    score={doc['score']:.3f} | {doc['text'][:80]}")


async def main():
    print("=" * 60)
    print("ROGER — Gerstmann RAG Indexer")
    print("=" * 60)

    await index_biographical()
    await index_historical()
    await index_inventario()
    await test_search()

    print("\n" + "=" * 60)
    print("Done.")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
