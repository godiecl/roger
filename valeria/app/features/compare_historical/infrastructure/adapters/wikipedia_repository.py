import requests

from app.features.compare_historical.domain.historical_port import HistoricalPort

class WikipediaRepository(HistoricalPort):

    BASE_URL = "https://api.wikimedia.org/feed/v1/wikipedia"

    def get_events_by_date(
        self,
        month: int,
        day: int,
        lang: str = "es"
    ) -> list[dict]:

        url = (
            f"{self.BASE_URL}/"
            f"{lang}/onthisday/events/"
            f"{month:02d}/{day:02d}"
        )

        response = requests.get(
            url,
            headers={
                "User-Agent": "RogerAI/1.0"
            },
            timeout=10
        )

        response.raise_for_status()

        data = response.json()

        return data.get("events", [])