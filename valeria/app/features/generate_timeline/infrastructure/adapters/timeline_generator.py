"""
TimelineGenerator — genera la línea de tiempo contextual de una fotografía.

El eje historical lo cubre WikipediaEnricher con datos reales (VERAZ).
El LLM solo genera los ejes biographical y expedition (VEROSIMIL).
Cuando el RAG esté poblado, biographical y expedition también se enriquecerán.
"""

import json
import time
from typing import List, Optional

import structlog

from app.features.generate_timeline.domain.timeline import (
    EventType, SourceType, Timeline, TimelineAxis, TimelineEvent,
)
from app.features.generate_timeline.domain.timeline_port import ITimelineGenerator
from app.infrastructure.ai.llm.llm_factory import create_llm_provider

logger = structlog.get_logger()

_SYSTEM_PROMPT = """Eres un historiador experto en la vida y obra de Robert Gerstmann (1886-1964),
fotógrafo alemán que documentó Sudamérica entre 1920 y 1964. Conoces en detalle:
- Su biografía, viajes y expediciones
- El contexto histórico de Chile y Sudamérica en el siglo XX
- Los eventos políticos, culturales y sociales de la época

Tu tarea es generar una línea de tiempo contextual para una fotografía específica,
situándola en su contexto histórico de manera rigurosa y educativa.

Responde ÚNICAMENTE con JSON válido, sin texto adicional."""

_USER_PROMPT_TEMPLATE = """Genera el contexto biográfico y de expedición para esta fotografía de Robert Gerstmann:

Fecha aproximada: {date}
Ubicación: {location}
Descripción: {description}
Objetos detectados: {objects}
{historical_note}
Crea entre 3 y 5 eventos en los ejes biographical y expedition solamente.
NO incluyas eventos del eje historical — esos se obtienen de fuentes verificadas externas.

Responde con este JSON exacto:
{{
  "context_summary": "Párrafo introductorio (3-4 oraciones) que contextualiza esta fotografía en relación a la vida y obra de Gerstmann",
  "events": [
    {{
      "date_label": "Marzo 1928",
      "year": 1928,
      "title": "Título del evento",
      "description": "Descripción del evento (1-2 oraciones)",
      "axis": "biographical|expedition",
      "event_type": "travel|personal|cultural|other",
      "source_type": "verosimil"
    }}
  ]
}}

Todos los eventos deben usar source_type="verosimil"."""


class TimelineGenerator(ITimelineGenerator):

    def __init__(self):
        self._llm = create_llm_provider()

    @property
    def provider_name(self) -> str:
        return self._llm.provider_name

    async def generate(
        self,
        photograph_id: int,
        photograph_date: Optional[str],
        photograph_location: Optional[str],
        photograph_description: Optional[str],
        detected_objects: Optional[List[str]],
        wikipedia_events: Optional[List[TimelineEvent]] = None,
    ) -> Timeline:
        start = time.time()
        wikipedia_events = wikipedia_events or []

        historical_note = (
            f"Contexto histórico verificado disponible: {len(wikipedia_events)} eventos del período "
            f"({wikipedia_events[0].year}–{wikipedia_events[-1].year}).\n"
            if wikipedia_events else ""
        )

        user_prompt = _USER_PROMPT_TEMPLATE.format(
            date=photograph_date or "Desconocida (estimada entre 1920-1964)",
            location=photograph_location or "Sudamérica (ubicación exacta no determinada)",
            description=photograph_description or "Sin descripción disponible",
            objects=", ".join(detected_objects) if detected_objects else "No detectados",
            historical_note=historical_note,
        )

        try:
            raw = await self._llm.complete([
                {"role": "system", "content": _SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ])
            llm_events, context_summary = self._parse_response(raw)
        except Exception as e:
            logger.error("Generación de timeline fallida", error=str(e), photograph_id=photograph_id)
            llm_events = self._fallback_events(photograph_date, photograph_location)
            context_summary = (
                "No fue posible generar el contexto biográfico completo. "
                "Se muestran eventos de referencia generales sobre la obra de Robert Gerstmann."
            )

        generation_time_ms = int((time.time() - start) * 1000)

        return Timeline(
            photograph_id=photograph_id,
            events=wikipedia_events + llm_events,
            provider=self.provider_name,
            context_summary=context_summary,
            generation_time_ms=generation_time_ms,
        )

    def _parse_response(self, raw: str):
        raw = raw.strip()
        if raw.startswith("```"):
            lines = raw.split("\n")
            raw = "\n".join(lines[1:-1] if lines[-1].strip() == "```" else lines[1:])

        data = json.loads(raw)
        context_summary = data.get("context_summary", "")

        events = []
        for e in data.get("events", []):
            try:
                axis = TimelineAxis(e.get("axis", "historical"))
            except ValueError:
                axis = TimelineAxis.HISTORICAL

            try:
                event_type = EventType(e.get("event_type", "other"))
            except ValueError:
                event_type = EventType.OTHER

            try:
                source_type = SourceType(e.get("source_type", "verosimil"))
            except ValueError:
                source_type = SourceType.VEROSIMIL

            events.append(TimelineEvent(
                date_label=e.get("date_label", ""),
                year=e.get("year"),
                title=e.get("title", ""),
                description=e.get("description", ""),
                axis=axis,
                event_type=event_type,
                source_type=source_type,
            ))

        return events, context_summary

    def _fallback_events(
        self,
        date: Optional[str],
        location: Optional[str],
    ) -> List[TimelineEvent]:
        return [
            TimelineEvent(
                date_label="1886",
                year=1886,
                title="Nacimiento de Robert Gerstmann",
                description="Robert Gerstmann nace en Alemania. Se convertiría en uno de los fotógrafos más importantes de Sudamérica.",
                axis=TimelineAxis.BIOGRAPHICAL,
                event_type=EventType.PERSONAL,
                source_type=SourceType.VERAZ,
            ),
            TimelineEvent(
                date_label="1920s",
                year=1920,
                title="Llegada a Sudamérica",
                description="Gerstmann se establece en Sudamérica e inicia su trabajo de documentación fotográfica del continente.",
                axis=TimelineAxis.BIOGRAPHICAL,
                event_type=EventType.TRAVEL,
                source_type=SourceType.VERAZ,
            ),
            TimelineEvent(
                date_label="1964",
                year=1964,
                title="Fallecimiento de Robert Gerstmann",
                description="Robert Gerstmann fallece dejando un legado de más de 40.000 fotografías del continente sudamericano.",
                axis=TimelineAxis.BIOGRAPHICAL,
                event_type=EventType.PERSONAL,
                source_type=SourceType.VERAZ,
            ),
        ]
