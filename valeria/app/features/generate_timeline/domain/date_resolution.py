from dataclasses import dataclass
from typing import Literal


@dataclass
class DateResolution:
    year_min: int
    year_max: int
    source: Literal["metadata", "rag", "clip", "none"]
    confidence: float

    @property
    def is_resolved(self) -> bool:
        return self.source != "none" and self.year_min > 0

    @property
    def midpoint(self) -> int:
        return (self.year_min + self.year_max) // 2

    @property
    def label(self) -> str:
        if self.year_min == self.year_max:
            return str(self.year_min)
        return f"{self.year_min}–{self.year_max}"
