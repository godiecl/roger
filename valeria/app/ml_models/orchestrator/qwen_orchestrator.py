import re
import json


class QwenOrchestrator:
    """
    Orquestador textual inicial.
    Por ahora usa reglas simples, luego se puede reemplazar por Qwen real.
    """

    def decide(self, message: str):
        msg = message.lower()

        image_name = self._extract_image_name(message)
        top_k = self._extract_top_k(message, default=5)

        if any(word in msg for word in [
            "describe",
            "describir",
            "qué aparece",
            "que aparece",
            "lugar",
            "escena",
            "analiza la imagen",
            "interpreta"
        ]):
            return {
                "tool": "descripcion_visual",
                "args": {
                    "image": image_name
                }
            }

        if any(word in msg for word in [
            "similar",
            "similares",
            "parecida",
            "parecidas",
            "relacionadas con esta imagen"
        ]):
            return {
                "tool": "busqueda_visual_similaridad",
                "args": {
                    "image": image_name,
                    "top_k": top_k
                }
            }

        if any(word in msg for word in ["barco", "barcos", "bote", "botes"]):
            return {
                "tool": "busqueda_semantica_texto",
                "args": {
                    "query": "boats",
                    "top_k": top_k
                }
            }

        if any(word in msg for word in ["persona", "personas", "gente"]):
            return {
                "tool": "busqueda_semantica_texto",
                "args": {
                    "query": "people",
                    "top_k": top_k
                }
            }

        if any(word in msg for word in ["puerto", "muelle"]):
            return {
                "tool": "busqueda_semantica_texto",
                "args": {
                    "query": "harbor",
                    "top_k": top_k
                }
            }

        if any(word in msg for word in ["edificio", "edificios", "arquitectura", "calle"]):
            return {
                "tool": "busqueda_semantica_texto",
                "args": {
                    "query": "buildings street architecture",
                    "top_k": top_k
                }
            }

        if any(word in msg for word in ["tren", "ferrocarril"]):
            return {
                "tool": "busqueda_semantica_texto",
                "args": {
                    "query": "train railway",
                    "top_k": top_k
                }
            }

        if any(word in msg for word in ["texto", "leer", "fecha", "inscripción", "inscripcion", "ocr"]):
            return {
                "tool": "ocr",
                "args": {
                    "image": image_name
                }
            }

        if any(word in msg for word in ["objeto", "objetos", "detecta", "detectar", "identifica"]):
            return {
                "tool": "deteccion_objetos",
                "args": {
                    "image": image_name
                }
            }

        if any(word in msg for word in [
            "deterioro",
            "daño",
            "daño",
            "rayón",
            "rayon",
            "mancha",
            "blur",
            "calidad"
        ]):
            return {
                "tool": "deterioro",
                "args": {
                    "image": image_name
                }
            }

        return {
            "tool": "chat",
            "args": {}
        }

    def _extract_image_name(self, text: str):
        match = re.search(r"[\w\-]+?\.(jpg|jpeg|png|webp)", text, re.IGNORECASE)
        return match.group(0) if match else None

    def _extract_top_k(self, text: str, default: int = 5):
        match = re.search(r"\b\d+\b", text)
        return int(match.group(0)) if match else default

    def extract_json(self, text: str):
        match = re.search(r"\{.*\}", text, re.DOTALL)

        if not match:
            return None

        try:
            return json.loads(match.group())
        except Exception:
            return None