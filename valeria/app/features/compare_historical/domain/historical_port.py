from abc import ABC, abstractmethod

class HistoricalPort(ABC):

    @abstractmethod
    def get_events_by_date(
        self,
        month: int,
        day: int,
        lang: str = "es"
    ) -> list[dict]:
        pass