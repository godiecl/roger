import os
import cv2
import easyocr


class OCRService:
    def __init__(self):
        self.reader = easyocr.Reader(
            ["es", "en"],
            gpu=False
        )

    def analyze(self, image_path: str):
        if not os.path.exists(image_path):
            return {
                "error": f"No existe la imagen: {image_path}"
            }

        results = self.reader.readtext(image_path)

        texts = []

        for bbox, text, conf in results:
            texts.append({
                "text": text,
                "confidence": float(conf),
                "bbox": bbox
            })

        blur_score = self._estimate_blur(image_path)

        return {
            "image_name": os.path.basename(image_path),
            "texts": texts,
            "blur_score": blur_score
        }

    def _estimate_blur(self, image_path: str):
        img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)

        if img is None:
            return None

        return float(cv2.Laplacian(img, cv2.CV_64F).var())