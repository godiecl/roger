"""
Places365 analyzer for Attribute 04 — Environmental & Spatial Context.

Uses ResNet50 pretrained on Places365 to classify the scene type of a photograph
and map it to the ROGER taxonomy (setting_type, specific_typology, conservation_state).

Dependencies:  pip install torch torchvision Pillow
Activate with: ATTR04_ANALYZER=places365  in .env

Model weights (~100 MB) and category list are downloaded on first use
to ~/.cache/roger/places365/.
"""

import os
import urllib.request
from pathlib import Path
from typing import Optional

from app.infrastructure.analysis.base_analyzer import IAttributeAnalyzer

PROVIDER_NAME = "places365"
PROVIDER_VERSION = "resnet50"

_CACHE_DIR = Path.home() / ".cache" / "roger" / "places365"
_WEIGHTS_URL = (
    "http://places2.csail.mit.edu/models_places365/resnet50_places365.pth.tar"
)
_CATEGORIES_URL = (
    "https://raw.githubusercontent.com/csailvision/places365/master/categories_places365.txt"
)

# Keywords that identify interior scenes
_INTERIOR_KW = {
    "room", "bedroom", "bathroom", "kitchen", "dining", "living",
    "office", "library", "hospital", "hotel", "restaurant", "cafe",
    "corridor", "hallway", "staircase", "basement", "attic", "cloister",
    "subway", "store", "supermarket", "conference", "archive", "bar",
    "classroom", "gym", "arena_indoor", "church_indoor", "museum_indoor",
    "auditorium", "ballroom", "casino", "closet", "cockpit",
}

# Keywords that identify natural scenes
_NATURAL_KW = {
    "forest", "mountain", "beach", "desert", "river", "lake", "ocean",
    "coast", "shore", "cliff", "canyon", "valley", "field", "meadow",
    "swamp", "marsh", "waterfall", "cave", "glacier", "iceberg",
    "rainforest", "prairie", "tundra", "reef", "creek", "stream",
    "savanna", "bayou", "delta", "pond", "bog", "heath", "moor",
    "tide_flat", "sandbar", "sky", "volcano", "butte", "islet",
}


def _map_category(category: str) -> tuple[Optional[str], str]:
    """Return (setting_type, specific_typology) from a Places365 category label."""
    cat = category.lower().replace("/", "_").replace("-", "_")
    typology = cat.replace("_", " ").strip()
    for kw in _INTERIOR_KW:
        if kw in cat:
            return "interior", typology
    for kw in _NATURAL_KW:
        if kw in cat:
            return "natural", typology
    return "urban", typology


def _conservation_from_setting(setting: Optional[str]) -> Optional[str]:
    if setting == "natural":
        return "pristine"
    if setting == "urban":
        return "anthropogenic"
    return None


class Places365Analyzer(IAttributeAnalyzer):
    provider_name = PROVIDER_NAME
    provider_version = PROVIDER_VERSION

    def __init__(self) -> None:
        try:
            import torch  # noqa: F401
            import torchvision  # noqa: F401
        except ImportError as exc:
            raise ImportError(
                "Places365Analyzer requires: pip install torch torchvision Pillow. "
                "Or set ATTR04_ANALYZER=stub to disable scene classification."
            ) from exc

        self._model = None
        self._categories: list[str] = []

    def _load(self) -> None:
        """Lazy-load model weights on first use."""
        import torch
        import torchvision.models as models

        _CACHE_DIR.mkdir(parents=True, exist_ok=True)

        categories_path = _CACHE_DIR / "categories_places365.txt"
        if not categories_path.exists():
            urllib.request.urlretrieve(_CATEGORIES_URL, categories_path)

        with open(categories_path) as fh:
            # Format: "/a/abbey 0" — strip leading path component and index
            self._categories = [
                line.strip().split(" ")[0].split("/")[-1]
                for line in fh
                if line.strip()
            ]

        weights_path = _CACHE_DIR / "resnet50_places365.pth.tar"
        if not weights_path.exists():
            urllib.request.urlretrieve(_WEIGHTS_URL, weights_path)

        arch = models.resnet50(num_classes=365)
        checkpoint = torch.load(weights_path, map_location="cpu")
        state_dict = {
            k.replace("module.", ""): v
            for k, v in checkpoint["state_dict"].items()
        }
        arch.load_state_dict(state_dict)
        arch.eval()
        self._model = arch

    def analyze(self, file_path: str) -> dict:
        if not os.path.exists(file_path):
            return {
                "error": f"File not found: {file_path}",
                "provider": self.provider_name,
                "provider_version": self.provider_version,
            }
        try:
            if self._model is None:
                self._load()

            from PIL import Image
            import torch
            import torch.nn.functional as F
            import torchvision.transforms as transforms

            transform = transforms.Compose([
                transforms.Resize((256, 256)),
                transforms.CenterCrop(224),
                transforms.ToTensor(),
                transforms.Normalize(
                    mean=[0.485, 0.456, 0.406],
                    std=[0.229, 0.224, 0.225],
                ),
            ])

            tensor = transform(Image.open(file_path).convert("RGB")).unsqueeze(0)

            with torch.no_grad():
                logits = self._model(tensor)
                probs = F.softmax(logits, dim=1).squeeze(0)

            top5_prob, top5_idx = probs.topk(5)
            best_category = self._categories[int(top5_idx[0])]
            confidence = float(top5_prob[0])

            setting_type, specific_typology = _map_category(best_category)
            conservation_state = _conservation_from_setting(setting_type)

            raw = {
                self._categories[int(top5_idx[i])]: round(float(top5_prob[i]), 4)
                for i in range(len(top5_idx))
            }

            return {
                "setting_type": setting_type,
                "specific_typology": specific_typology,
                "conservation_state": conservation_state,
                "human_env_relationship": None,
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
