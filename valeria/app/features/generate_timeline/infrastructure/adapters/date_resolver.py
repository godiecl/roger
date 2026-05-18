from datetime import date, datetime
from typing import Optional
import re

import structlog
from sqlalchemy.ext.asyncio import AsyncSession

from app.features.generate_timeline.domain.date_resolution import DateResolution
from app.features.taxonomy.infrastructure.adapters.taxonomy_repository import TaxonomyRepository
from app.infrastructure.rag.knowledge_base.biographical_kb import biographical_kb

logger = structlog.get_logger()

_RAG_SCORE_THRESHOLD = 0.40
_RAG_CONFIDENCE_FACTOR = 0.65


class DateResolver:

    def __init__(self, session: AsyncSession):
        self._taxonomy = TaxonomyRepository(session)

    async def resolve(self, photograph_id: int, context: str = "") -> DateResolution:
        # Nivel 1 — metadata directa de taxonomía
        try:
            chronology = await self._taxonomy.get_active_chronology(photograph_id)
        except Exception as e:
            logger.warning("Error leyendo taxonomía cronológica", photograph_id=photograph_id, error=str(e))
            return await self._resolve_from_rag(photograph_id, context)

        if not chronology:
            return await self._resolve_from_rag(photograph_id, context)

        confidence = chronology.confidence_level or 0.8

        if chronology.precise_date:
            year = _to_year(chronology.precise_date)
            if year:
                return DateResolution(year_min=year, year_max=year, source="metadata", confidence=confidence)

        if chronology.date_from and chronology.date_to:
            year_from = _to_year(chronology.date_from)
            year_to = _to_year(chronology.date_to)
            if year_from and year_to:
                return DateResolution(year_min=year_from, year_max=year_to, source="metadata", confidence=confidence)

        if chronology.date_from:
            year = _to_year(chronology.date_from)
            if year:
                return DateResolution(year_min=year, year_max=year + 5, source="metadata", confidence=confidence * 0.6)

        return await self._resolve_from_rag(photograph_id, context)

    async def _resolve_from_rag(self, photograph_id: int, context: str) -> DateResolution:
        # Nivel 2 — búsqueda semántica en KB biográfica
        if not context.strip():
            return _none()
        try:
            results = await biographical_kb.search(context, n_results=3)
            hits = [r for r in results if r["score"] >= _RAG_SCORE_THRESHOLD]
            if not hits:
                return _none()

            top = hits[0]
            meta = top["metadata"]
            year_min = _to_year(meta.get("fecha_inicio"))
            year_max = _to_year(meta.get("fecha_fin")) or year_min

            if not year_min:
                return _none()

            # Si hay varios hits con buena puntuación, ampliar el rango
            for hit in hits[1:]:
                m = hit["metadata"]
                yi = _to_year(m.get("fecha_inicio"))
                yf = _to_year(m.get("fecha_fin")) or yi
                if yi:
                    year_min = min(year_min, yi)
                if yf:
                    year_max = max(year_max, yf)

            confidence = top["score"] * _RAG_CONFIDENCE_FACTOR
            logger.info(
                "Fecha estimada por RAG",
                photograph_id=photograph_id,
                year_min=year_min,
                year_max=year_max,
                score=round(top["score"], 3),
            )
            return DateResolution(year_min=year_min, year_max=year_max, source="rag", confidence=confidence)

        except Exception as e:
            logger.warning("Error en resolución RAG", photograph_id=photograph_id, error=str(e))
            return _none()


def _none() -> DateResolution:
    return DateResolution(year_min=0, year_max=0, source="none", confidence=0.0)


def _to_year(value) -> Optional[int]:
    if value is None:
        return None
    if isinstance(value, int):
        return value
    if isinstance(value, (date, datetime)):
        return value.year
    if isinstance(value, str):
        # Formato directo
        for fmt in ("%Y-%m-%d", "%Y-%m", "%Y"):
            try:
                return datetime.strptime(value[:len(fmt)], fmt).year
            except ValueError:
                continue
        # Extraer primer número de 4 dígitos (ej. "mayo 1925", "temporada 1947/48")
        m = re.search(r"\b(1[89]\d{2}|20\d{2})\b", value)
        if m:
            return int(m.group(1))
    return None
