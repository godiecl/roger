"""
CLIP-based temporal analyzer for Attribute 02 — Chronological Dating.

Uses open_clip zero-shot classification to estimate the decade a photograph
was taken by comparing the image against a set of decade-labelled text prompts.

Dependencies:  pip install open-clip-torch torch Pillow
Activate with: ATTR02_ANALYZER=clip  in .env

First run downloads ~350 MB of CLIP weights to the torch cache.
"""

import os
from app.infrastructure.analysis.base_analyzer import IAttributeAnalyzer

PROVIDER_NAME = "clip_temporal"
PROVIDER_VERSION = "open_clip/ViT-B-32"

# (date_from ISO, date_to ISO, display label)
_DECADES: list[tuple[str, str, str]] = [
    ("1870-01-01", "1879-12-31", "1870s"),
    ("1880-01-01", "1889-12-31", "1880s"),
    ("1890-01-01", "1899-12-31", "1890s"),
    ("1900-01-01", "1909-12-31", "1900s"),
    ("1910-01-01", "1919-12-31", "1910s"),
    ("1920-01-01", "1929-12-31", "1920s"),
    ("1930-01-01", "1939-12-31", "1930s"),
    ("1940-01-01", "1949-12-31", "1940s"),
    ("1950-01-01", "1959-12-31", "1950s"),
    ("1960-01-01", "1969-12-31", "1960s"),
    ("1970-01-01", "1979-12-31", "1970s"),
    ("1980-01-01", "1989-12-31", "1980s"),
    ("1990-01-01", "1999-12-31", "1990s"),
    ("2000-01-01", "2009-12-31", "2000s"),
    ("2010-01-01", "2019-12-31", "2010s"),
]


class CLIPTemporalAnalyzer(IAttributeAnalyzer):
    provider_name = PROVIDER_NAME
    provider_version = PROVIDER_VERSION

    def __init__(self) -> None:
        try:
            import open_clip  # noqa: F401
            import torch  # noqa: F401
        except ImportError as exc:
            raise ImportError(
                "CLIPTemporalAnalyzer requires: pip install open-clip-torch torch Pillow. "
                "Or set ATTR02_ANALYZER=stub to disable temporal analysis."
            ) from exc

        import open_clip
        import torch

        self._torch = torch
        self._model, _, self._preprocess = open_clip.create_model_and_transforms(
            "ViT-B-32", pretrained="openai"
        )
        self._tokenizer = open_clip.get_tokenizer("ViT-B-32")
        self._model.eval()

    def analyze(self, file_path: str) -> dict:
        if not os.path.exists(file_path):
            return {
                "error": f"File not found: {file_path}",
                "provider": self.provider_name,
                "provider_version": self.provider_version,
            }
        try:
            from PIL import Image
            import torch.nn.functional as F

            image = self._preprocess(Image.open(file_path).convert("RGB")).unsqueeze(0)
            prompts = [
                f"a historical photograph taken in the {label}"
                for _, _, label in _DECADES
            ]
            text_tokens = self._tokenizer(prompts)

            with self._torch.no_grad():
                img_features = self._model.encode_image(image)
                txt_features = self._model.encode_text(text_tokens)
                logits = (img_features @ txt_features.T).squeeze(0)
                probs = F.softmax(logits, dim=0).tolist()

            best_idx = int(max(range(len(probs)), key=lambda i: probs[i]))
            confidence = float(probs[best_idx])
            date_from, date_to, label = _DECADES[best_idx]

            raw = {lbl: round(p, 4) for (_, _, lbl), p in zip(_DECADES, probs)}

            return {
                "date_type": "range",
                "precise_date": None,
                "date_from": date_from,
                "date_to": date_to,
                "date_hypothesis": (
                    f"Estimated decade: {label} (confidence {confidence:.0%})"
                ),
                "methodology": "CLIP zero-shot decade classification via open_clip ViT-B/32",
                "visual_evidence_notes": None,
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
