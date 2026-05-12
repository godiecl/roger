from datetime import datetime

from app.features.compare_historical.domain.historical_port import HistoricalPort

class CompareHistoricalUseCase:

    def __init__(self, historical_port: HistoricalPort):
        self.historical_port = historical_port

    def execute(
        self,
        dates: list[str],
        lang: str = "es",
        limit_per_date: int = 5
    ):

        result = []

        for date_str in dates:

            parsed_date = datetime.strptime(
                date_str,
                "%Y-%m-%d"
            )

            events = self.historical_port.get_events_by_date(
                month=parsed_date.month,
                day=parsed_date.day,
                lang=lang
            )

            result.append({
                "date": date_str,
                "events": [
                    {
                        "year": event.get("year"),
                        "text": event.get("text"),
                        "image_url": self._get_event_image(event),
                        "page_url": self._get_event_page_url(event),
                    }
                    for event in events[:limit_per_date]
                ]
            })

        return result
    
    def _get_event_image(self, event: dict) -> str | None:
        pages = event.get("pages", [])

        for page in pages:
            thumbnail = page.get("thumbnail")
            if thumbnail and thumbnail.get("source"):
                return thumbnail.get("source")

            original_image = page.get("originalimage")
            if original_image and original_image.get("source"):
                return original_image.get("source")

        return None


    def _get_event_page_url(self, event: dict) -> str | None:
        pages = event.get("pages", [])

        for page in pages:
            content_urls = page.get("content_urls", {})
            desktop = content_urls.get("desktop", {})

            if desktop.get("page"):
                return desktop.get("page")

        return None