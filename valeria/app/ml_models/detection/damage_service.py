import os
import cv2


class DamageService:
    def analyze(self, image_path: str):
        if not os.path.exists(image_path):
            return {
                "error": f"No existe la imagen: {image_path}"
            }

        img = cv2.imread(image_path)

        if img is None:
            return {
                "error": "No se pudo leer la imagen.",
                "image_path": image_path
            }

        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        blur_score = cv2.Laplacian(gray, cv2.CV_64F).var()

        edges = cv2.Canny(gray, 80, 180)
        edge_density = edges.mean() / 255

        if blur_score < 80:
            diagnosis = "posible baja nitidez, blur o deterioro de digitalización"
        elif edge_density > 0.18:
            diagnosis = "posibles rayones, textura deteriorada o bordes muy marcados"
        else:
            diagnosis = "sin deterioro evidente en análisis básico"

        return {
            "image_name": os.path.basename(image_path),
            "blur_score": float(blur_score),
            "edge_density": float(edge_density),
            "diagnosis": diagnosis
        }