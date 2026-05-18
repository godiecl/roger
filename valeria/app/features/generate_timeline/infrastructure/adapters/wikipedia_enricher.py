from typing import List

import httpx
import structlog

from app.features.generate_timeline.domain.date_resolution import DateResolution
from app.features.generate_timeline.domain.timeline import (
    EventType,
    SourceType,
    TimelineAxis,
    TimelineEvent,
)

logger = structlog.get_logger()

_BASE_URL = "https://api.wikimedia.org/feed/v1/wikipedia"
_HEADERS = {"User-Agent": "RogerAI/1.0"}
_TIMEOUT = 8.0
_MAX_EVENTS = 5
# Cuatro fechas representativas distribuidas en el año
_SAMPLE_DATES = [(3, 15), (6, 15), (9, 15), (12, 15)]


class WikipediaEnricher:

    async def enrich(self, resolution: DateResolution, lang: str = "es") -> List[TimelineEvent]:
        if not resolution.is_resolved:
            return []

        collected: list = []

        async with httpx.AsyncClient(timeout=_TIMEOUT, headers=_HEADERS) as client:
            for month, day in _SAMPLE_DATES:
                if len(collected) >= _MAX_EVENTS:
                    break
                try:
                    raw = await self._fetch(client, month, day, lang)
                    in_range = [
                        e for e in raw
                        if e.get("year") and resolution.year_min <= e["year"] <= resolution.year_max
                    ]
                    collected.extend(in_range)
                except Exception as e:
                    logger.debug("Wikipedia query fallida", month=month, day=day, error=str(e))

        return _to_events(collected[:_MAX_EVENTS])

    async def _fetch(self, client: httpx.AsyncClient, month: int, day: int, lang: str) -> list:
        url = f"{_BASE_URL}/{lang}/onthisday/events/{month:02d}/{day:02d}"
        resp = await client.get(url)
        resp.raise_for_status()
        return resp.json().get("events", [])


def _to_events(raw_events: list) -> List[TimelineEvent]:
    events = []
    for e in raw_events:
        year = e.get("year")
        text = e.get("text", "").strip()
        if not year or not text:
            continue
        events.append(TimelineEvent(
            date_label=str(year),
            year=year,
            title=_first_sentence(text),
            description=text,
            axis=TimelineAxis.HISTORICAL,
            event_type=EventType.HISTORICAL,
            source_type=SourceType.VERAZ,
        ))
    return events


def _first_sentence(text: str) -> str:
    sentence = text.split(".")[0].strip()
    return sentence[:80] + "..." if len(sentence) > 80 else sentence
