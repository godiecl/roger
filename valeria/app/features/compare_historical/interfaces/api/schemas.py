from pydantic import BaseModel

class CompareHistoricalRequest(BaseModel):
    dates: list[str]
    lang: str = "es"
    limit_per_date: int = 5