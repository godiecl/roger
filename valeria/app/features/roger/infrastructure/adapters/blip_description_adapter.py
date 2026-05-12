import os
from pathlib import Path

from app.features.roger.domain.roger_port import IVisualDescriptionService
from app.ml_models.captioning.blip_services import BlipService


class BlipDescriptionAdapter(IVisualDescriptionService):
    def __init__(self):
        BASE_DIR = Path(__file__).resolve().parents[5]
        self.image_dir = BASE_DIR / "data" / "roger" / "images"
        self.blip_service = BlipService()

    async def describe(self, image_name: str):
        image_path = self.image_dir / image_name

        if not image_path.exists():
            return {
                "error": f"No existe la imagen: {image_name}",
                "image_path": str(image_path)
            }

        return self.blip_service.describe(str(image_path))