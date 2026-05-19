"""
CollectionNarrativeGenerator — genera una narrativa temporal unificada
para una colección de fotografías agrupadas por clustering visual.

FONDEF Módulo 6 — Generación de Conocimiento:
  Narrativa de la colección completa con ordenamiento cronológico de clusters.
"""

import json
import time
from typing import List, Optional

import structlog

from app.features.generate_timeline.domain.timeline import (
    CollectionClusterSummary, CollectionNarrative,
)
from app.infrastructure.ai.llm.llm_factory import create_llm_provider

logger = structlog.get_logger()

_SYSTEM_PROMPT = """Eres un historiador y curador experto en la obra de Robert Gerstmann (1886–1964),
fotógrafo alemán que documentó Sudamérica entre 1920 y 1964.

Tu tarea es analizar un conjunto de grupos visuales (clusters) de fotografías ordenados
cronológicamente y generar una narrativa cohesiva que describa el arco temporal de la
colección: qué estaba documentando Gerstmann, cómo evolucionó su trabajo, qué historia
colectiva cuentan estas imágenes en conjunto.

Responde ÚNICAMENTE con JSON válido, sin texto adicional."""

_USER_PROMPT_TEMPLATE = """Analiza esta colección de {n_clusters} grupos visuales de fotografías de Robert Gerstmann,
ordenados cronológicamente. La colección comprende {photograph_count} fotografías totales.
Período aproximado: {year_span}.

Grupos visuales (en orden cronológico):
{clusters_text}

Genera una narrativa que:
1. Introduzca el conjunto como un corpus histórico coherente
2. Describa el arco temporal: cómo evoluciona el trabajo documentado a lo largo del tiempo
3. Identifique temas o expediciones recurrentes entre los grupos
4. Contextualice el significado histórico del conjunto

Responde con este JSON exacto:
{{
  "collection_narrative": "Narrativa completa en 3-5 párrafos (400-600 palabras) en español",
  "temporal_arc": "Descripción concisa (2-3 oraciones) del arco temporal del corpus",
  "thematic_threads": ["hilo temático 1", "hilo temático 2", "hilo temático 3"],
  "historical_significance": "Párrafo sobre el significado histórico del conjunto para la memoria visual de Sudamérica"
}}"""


class CollectionNarrativeGenerator:

    def __init__(self):
        self._llm = create_llm_provider()

    @property
    def provider_name(self) -> str:
        return self._llm.provider_name

    async def generate(
        self,
        job_id: int,
        ordered_clusters: List[CollectionClusterSummary],
        photograph_count: int,
    ) -> CollectionNarrative:
        start = time.time()

        dated = [c for c in ordered_clusters if c.year_representative]
        year_min = min(c.year_min or c.year_representative for c in dated) if dated else None
        year_max = max(c.year_max or c.year_representative for c in dated) if dated else None

        if year_min and year_max:
            year_span = f"{year_min}–{year_max}" if year_min != year_max else str(year_min)
        else:
            year_span = "período no determinado (estimado 1920–1964)"

        clusters_text = _build_clusters_text(ordered_clusters)

        user_prompt = _USER_PROMPT_TEMPLATE.format(
            n_clusters=len(ordered_clusters),
            photograph_count=photograph_count,
            year_span=year_span,
            clusters_text=clusters_text,
        )

        try:
            raw = await self._llm.complete([
                {"role": "system", "content": _SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ])
            data = _parse_response(raw)
        except Exception as e:
            logger.error(
                "Generación de narrativa de colección fallida",
                job_id=job_id,
                error=str(e),
            )
            data = _fallback_data(len(ordered_clusters), year_span)

        generation_time_ms = int((time.time() - start) * 1000)

        return CollectionNarrative(
            job_id=job_id,
            collection_narrative=data["collection_narrative"],
            temporal_arc=data["temporal_arc"],
            thematic_threads=data["thematic_threads"],
            historical_significance=data["historical_significance"],
            ordered_clusters=ordered_clusters,
            photograph_count=photograph_count,
            provider=self.provider_name,
            generation_time_ms=generation_time_ms,
            year_min=year_min,
            year_max=year_max,
        )


def _build_clusters_text(clusters: List[CollectionClusterSummary]) -> str:
    lines = []
    for i, c in enumerate(clusters, 1):
        if c.year_representative:
            if c.year_min and c.year_max and c.year_min != c.year_max:
                date_str = f"ca. {c.year_representative} ({c.year_min}–{c.year_max})"
            else:
                date_str = str(c.year_representative)
        else:
            date_str = "fecha no determinada"
        lines.append(
            f"{i}. Grupo '{c.label}' — {c.photograph_count} fotografías — {date_str}"
        )
    return "\n".join(lines)


def _parse_response(raw: str) -> dict:
    raw = raw.strip()
    if raw.startswith("```"):
        lines = raw.split("\n")
        raw = "\n".join(lines[1:-1] if lines[-1].strip() == "```" else lines[1:])
    data = json.loads(raw)
    return {
        "collection_narrative": data.get("collection_narrative", ""),
        "temporal_arc": data.get("temporal_arc", ""),
        "thematic_threads": data.get("thematic_threads", []),
        "historical_significance": data.get("historical_significance", ""),
    }


def _fallback_data(n_clusters: int, year_span: str) -> dict:
    return {
        "collection_narrative": (
            f"Esta colección comprende {n_clusters} grupos visuales que abarcan el período {year_span}. "
            "El conjunto representa una parte del trabajo documental de Robert Gerstmann en Sudamérica. "
            "No fue posible generar la narrativa detallada automáticamente; se recomienda revisión manual."
        ),
        "temporal_arc": (
            f"La colección abarca el período {year_span}, reflejando distintas etapas del trabajo de Gerstmann."
        ),
        "thematic_threads": ["documentación geográfica", "retrato cultural", "expedición territorial"],
        "historical_significance": (
            "El corpus forma parte del archivo fotográfico patrimonial más completo sobre Sudamérica "
            "del siglo XX, con valor histórico para la memoria visual de la región."
        ),
    }
