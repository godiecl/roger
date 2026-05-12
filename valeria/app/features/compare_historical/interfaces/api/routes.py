from fastapi import APIRouter

from app.features.compare_historical.interfaces.api.schemas import (
    CompareHistoricalRequest
)

from app.features.compare_historical.application.compare_historical_usecase import (
    CompareHistoricalUseCase
)

from app.features.compare_historical.infrastructure.adapters.wikipedia_repository import (
    WikipediaRepository
)

router = APIRouter()

usecase = CompareHistoricalUseCase(
    historical_port=WikipediaRepository()
)


@router.post("/compare-historical")
def compare_historical(
    request: CompareHistoricalRequest
):

    return usecase.execute(
        dates=request.dates,
        lang=request.lang,
        limit_per_date=request.limit_per_date
    )