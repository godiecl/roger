"""
GeoCLIP analyzer for Attribute 03 — Geographic Reference.

Uses the GeoCLIP model to estimate where in the world a photograph was taken,
returning GPS coordinates (latitude, longitude) with a confidence score.

Dependencies:  pip install geoclip torch
Activate with: ATTR03_ANALYZER=geoclip  in .env

First run downloads GeoCLIP model weights (~1 GB) to the torch cache.
"""

import os
import torch
from app.infrastructure.analysis.base_analyzer import IAttributeAnalyzer


def _patch_geoclip_image_encoder() -> None:
    """
    Fix de compatibilidad con transformers >= 5.x.
    get_image_features() ahora devuelve BaseModelOutputWithPooling en vez de un Tensor,
    lo que rompe el MLP interno de GeoCLIP. Extraemos el tensor manualmente.
    """
    try:
        from geoclip.model.image_encoder import ImageEncoder

        original_forward = ImageEncoder.forward

        def patched_forward(self, x):
            x = self.CLIP.get_image_features(pixel_values=x)
            if not isinstance(x, torch.Tensor):
                x = x.pooler_output
            x = self.mlp(x)
            return x

        if ImageEncoder.forward is not patched_forward:
            ImageEncoder.forward = patched_forward
    except Exception:
        pass

PROVIDER_NAME = "geoclip"
PROVIDER_VERSION = "1"


class GeoCLIPAnalyzer(IAttributeAnalyzer):
    provider_name = PROVIDER_NAME
    provider_version = PROVIDER_VERSION

    def __init__(self) -> None:
        try:
            from geoclip import GeoCLIP as _GeoCLIP  # noqa: F401
        except ImportError as exc:
            raise ImportError(
                "GeoCLIPAnalyzer requires: pip install geoclip torch. "
                "Or set ATTR03_ANALYZER=stub to disable geographic analysis."
            ) from exc

        _patch_geoclip_image_encoder()
        from geoclip import GeoCLIP as _GeoCLIP
        self._model = _GeoCLIP()

    def analyze(self, file_path: str) -> dict:
        if not os.path.exists(file_path):
            return {
                "error": f"File not found: {file_path}",
                "provider": self.provider_name,
                "provider_version": self.provider_version,
            }
        try:
            top_gps, top_prob = self._model.predict(file_path, top_k=3)
            # top_gps: tensor (3, 2) with rows [lat, lon]
            # top_prob: tensor (3,) with probabilities

            best_lat = float(top_gps[0][0])
            best_lon = float(top_gps[0][1])
            confidence = float(top_prob[0])

            raw = [
                {
                    "lat": round(float(top_gps[i][0]), 6),
                    "lon": round(float(top_gps[i][1]), 6),
                    "prob": round(float(top_prob[i]), 4),
                }
                for i in range(len(top_prob))
            ]

            return {
                "location_type": "approximate",
                "geographic_location": f"{best_lat:.4f}, {best_lon:.4f}",
                "latitude": round(best_lat, 6),
                "longitude": round(best_lon, 6),
                "location_radius_km": None,
                "signage_found": None,
                "architectural_landmarks": None,
                "landscape_features": None,
                "confidence": round(confidence, 4),
                "raw_output": raw,
                "error": None,
                "provider": self.provider_name,
                "provider_version": self.provider_version,
            }

        except Exception as exc:
            return {
                "error": str(exc),
                "provider": self.provider_name,
                "provider_version": self.provider_version,
            }
