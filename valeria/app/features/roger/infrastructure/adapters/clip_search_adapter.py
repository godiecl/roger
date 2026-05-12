from pathlib import Path

from app.features.roger.domain.roger_port import ISemanticSearchService
from app.ml_models.embeddings.clip_search_service import ClipSearchService


class ClipSearchAdapter(ISemanticSearchService):

    def __init__(self):

        BASE_DIR = Path(__file__).resolve().parents[5]

        self.image_dir = BASE_DIR / "data" / "roger" / "images"

        self.clip_service = ClipSearchService(
            image_dir=str(self.image_dir)
        )

    async def search(self, query: str, top_k: int = 5):
        return self.clip_service.search(
            query=query,
            top_k=top_k
        )