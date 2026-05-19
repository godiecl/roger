"""
Index all RAG knowledge bases from the data/ directory.

Sources:
  data/gerstmann_timeline.json     → biographical_kb  (22 periods)
  data/gerstmann_descriptores.json → historical_kb    (CLIP descriptors + discrepancies)
  data/gerstmann_inventario_ucn.json → historical_kb  (UCN inventory items)

Usage:
  cd valeria/
  python scripts/index_knowledge_base.py
"""

import asyncio
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.infrastructure.rag.knowledge_base.biographical_kb import biographical_kb
from app.infrastructure.rag.knowledge_base.historical_kb import historical_kb


DATA_DIR = Path(__file__).parent.parent / "data"


# ── Biographical KB ────────────────────────────────────────────────────────────

def _timeline_to_docs(timeline: list) -> list:
    """Convert gerstmann_timeline.json entries to indexable documents."""
    docs = []
    for entry in timeline:
        places = ", ".join(entry.get("lugares", []))
        countries = ", ".join(entry.get("paises", []))
        series_titles = "; ".join(
            s.get("titulo", "") for s in entry.get("series", [])
        )
        publications = "; ".join(
            p.get("titulo", "") for p in entry.get("publicaciones", [])
        )

        parts = [
            f"{entry['titulo']} ({entry['fecha_inicio']}–{entry.get('fecha_fin', entry['fecha_inicio'])}).",
            entry.get("actividad", ""),
        ]
        if places:
            parts.append(f"Lugares: {places}.")
        if countries:
            parts.append(f"Países: {countries}.")
        if series_titles:
            parts.append(f"Series fotográficas: {series_titles}.")
        if publications:
            parts.append(f"Publicaciones: {publications}.")
        if entry.get("notas"):
            parts.append(f"Nota: {entry['notas']}")

        meta: dict = {
            "source": "gerstmann_timeline.json",
            "period_id": entry["id"],
            "type": "veraz" if entry.get("confianza") == "alta" else "verosimil",
            "category": "biographical",
            "countries": countries,
        }
        if entry.get("fecha_inicio") is not None:
            meta["year_from"] = entry["fecha_inicio"]
        if entry.get("fecha_fin") is not None:
            meta["year_to"] = entry["fecha_fin"]

        docs.append({
            "id": f"bio_{entry['id']}",
            "text": " ".join(p for p in parts if p.strip()),
            "metadata": meta,
        })
    return docs


# ── Historical KB ──────────────────────────────────────────────────────────────

def _descriptors_to_docs(data: dict) -> list:
    """Convert gerstmann_descriptores.json CLIP descriptors to documents."""
    docs = []
    for i, d in enumerate(data.get("descriptores_clip", [])):
        places = ", ".join(d.get("lugares", []))
        countries = ", ".join(d.get("paises_probables", []))
        ucn_ids = ", ".join(str(x) for x in d.get("ids_ucn_relevantes", []))
        periods = ", ".join(d.get("periodos_probables", []))

        parts = [
            f"Descriptor visual: {d['descriptor']}.",
            f"Países probables: {countries}." if countries else "",
            f"Lugares: {places}." if places else "",
            f"Años probables: {d.get('años_probables', '')}." if d.get("años_probables") else "",
            f"Períodos biográficos relacionados: {periods}." if periods else "",
            f"Ítems UCN relevantes: {ucn_ids}." if ucn_ids else "",
            d.get("notas", ""),
        ]

        docs.append({
            "id": f"clip_{i:03d}",
            "text": " ".join(p for p in parts if p.strip()),
            "metadata": {
                "source": "gerstmann_descriptores.json",
                "type": "verosimil",
                "category": "visual_descriptor",
                "countries": countries,
            },
        })

    for key in ("discrepancias_documentadas", "discrepancias"):
        for i, disc in enumerate(data.get(key, [])):
            text = f"Discrepancia documental: campo {disc.get('campo', '')}. "
            text += f"Fuente A ({disc.get('fuente_a', '')}): {disc.get('valor_a', '')}. "
            text += f"Fuente B ({disc.get('fuente_b', '')}): {disc.get('valor_b', '')}. "
            text += f"Decisión: {disc.get('decision', '')}."
            docs.append({
                "id": f"disc_{i:03d}",
                "text": text,
                "metadata": {
                    "source": "gerstmann_descriptores.json",
                    "type": "veraz",
                    "category": "discrepancy",
                },
            })

    return docs


def _inventory_to_docs(data: dict) -> list:
    """Convert UCN inventory items to documents (sample — index representative items)."""
    docs = []
    for item in data.get("items", []):
        title = item.get("titulo", "")
        support = item.get("soporte", "")
        color = "blanco y negro" if item.get("color") == "BW" else "color"
        neg = item.get("neg", 0)
        pos = item.get("pos", 0)
        tags = ", ".join(item.get("tags", []))

        text = (
            f"Ítem UCN Cajón {item['cajon']} ID {item['id']}: {title}. "
            f"Tipo: {item.get('tipo', '')}. Soporte: {support}. Fotografía en {color}. "
            f"Negativos: {neg}, positivos: {pos}."
        )
        if tags:
            text += f" Temas: {tags}."

        docs.append({
            "id": f"ucn_{item['cajon']}_{item['id']}",
            "text": text,
            "metadata": {
                "source": "gerstmann_inventario_ucn.json",
                "type": "veraz",
                "category": "inventory",
                "cajon": item["cajon"],
                "item_id": item["id"],
            },
        })
    return docs


# ── Main ───────────────────────────────────────────────────────────────────────

async def index_all():
    print("=" * 60)
    print("ROGER — Knowledge Base Indexer")
    print("=" * 60)

    # 1. Biographical KB
    timeline_path = DATA_DIR / "gerstmann_timeline.json"
    if timeline_path.exists():
        print("\n[1/3] Indexing biographical KB (gerstmann_timeline.json)…")
        timeline = json.loads(timeline_path.read_text(encoding="utf-8"))
        docs = _timeline_to_docs(timeline)
        ok = errors = 0
        for doc in docs:
            try:
                await biographical_kb.add_document(doc)
                ok += 1
            except Exception as e:
                print(f"  ERROR {doc['id']}: {e}")
                errors += 1
        print(f"  ✓ {ok} indexed, {errors} errors")
    else:
        print(f"  SKIP — {timeline_path} not found")

    # 2. Historical KB — CLIP descriptors + inventory
    desc_path = DATA_DIR / "gerstmann_descriptores.json"
    inv_path = DATA_DIR / "gerstmann_inventario_ucn.json"

    print("\n[2/3] Indexing historical KB (descriptores + inventario)…")
    hist_docs = []
    if desc_path.exists():
        data = json.loads(desc_path.read_text(encoding="utf-8"))
        hist_docs += _descriptors_to_docs(data)
    if inv_path.exists():
        data = json.loads(inv_path.read_text(encoding="utf-8"))
        hist_docs += _inventory_to_docs(data)

    ok = errors = 0
    for doc in hist_docs:
        try:
            await historical_kb.add_document(doc)
            ok += 1
        except Exception as e:
            print(f"  ERROR {doc['id']}: {e}")
            errors += 1
    print(f"  ✓ {ok} indexed, {errors} errors")

    # 3. Smoke test
    print("\n[3/3] Smoke test…")
    try:
        results = await biographical_kb.search("Gerstmann Bolivia mina fotografía", n_results=2)
        print(f"  biographical_kb → {len(results)} results")
        results = await historical_kb.search("Antofagasta norte Chile", n_results=2)
        print(f"  historical_kb   → {len(results)} results")
    except Exception as e:
        print(f"  search error: {e}")

    print("\n" + "=" * 60)
    print("Done.")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(index_all())
