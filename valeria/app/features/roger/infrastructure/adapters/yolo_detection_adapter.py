from pathlib import Path

from app.features.roger.domain.roger_port import IObjectDetectionService
from app.ml_models.detection.yolo_service import YOLOService


class YOLODetectionAdapter(IObjectDetectionService):

    def __init__(self):

        BASE_DIR = Path(__file__).resolve().parents[5]

        self.image_dir = BASE_DIR / "data" / "roger" / "images"
        self.service = YOLOService()

    async def detect(self, image_name: str):

        image_path = self.image_dir / image_name

        if not image_path.exists():
            return {
                "error": f"No existe la imagen: {image_name}",
                "image_path": str(image_path)
            }

        return self.service.detect(str(image_path))