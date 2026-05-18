from typing import Optional
from app.features.generate_context.domain.context import ImageContext
from app.features.generate_context.domain.context_port import IContextGenerator, IContextRepository


class GenerateContextUseCase:
    def __init__(self, generator: IContextGenerator, repository: IContextRepository):
        self._generator = generator
        self._repository = repository

    async def execute(
        self,
        image_id: int,
        title: Optional[str] = None,
        description: Optional[str] = None,
        year: Optional[int] = None,
        location: Optional[str] = None,
    ) -> ImageContext:
        context = await self._generator.generate(
            image_id=image_id,
            title=title,
            description=description,
            year=year,
            location=location,
        )
        return await self._repository.save(context)
