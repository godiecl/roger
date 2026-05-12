import os
from ultralytics import YOLO


class YOLOService:
    def __init__(self):
        self.model = YOLO("yolov8n.pt")

    def detect(self, image_path: str):
        if not os.path.exists(image_path):
            return {
                "error": f"No existe la imagen: {image_path}"
            }

        results = self.model(image_path)

        detections = []

        for r in results:
            for box in r.boxes:
                cls_id = int(box.cls[0])
                label = self.model.names[cls_id]
                conf = float(box.conf[0])
                xyxy = box.xyxy[0].cpu().numpy().tolist()

                detections.append({
                    "label": label,
                    "confidence": conf,
                    "box": xyxy
                })

        return {
            "image_name": os.path.basename(image_path),
            "detections": detections,
            "count": len(detections)
        }