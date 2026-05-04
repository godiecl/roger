"""
Pillow-based technical metadata extractor for ROGER.
Supports JPG and TIFF files. CR3 (raw Canon) is read via ExifTool when available.
Returns a structured dict; never raises — errors go in the 'error' key.
"""

import os
import subprocess
import json
from typing import Any, Optional


# EXIF tag IDs we care about
_EXIF_TAGS = {
    271: "Make",
    272: "Model",
    33434: "ExposureTime",
    33437: "FNumber",
    34855: "ISOSpeedRatings",
    37386: "FocalLength",
    42036: "LensModel",
    306: "DateTime",
    36867: "DateTimeOriginal",
}

PROVIDER_NAME = "pillow"
PROVIDER_VERSION = "12"


def _fraction_to_str(value: Any) -> Optional[str]:
    """Convert PIL IFDRational or tuple fraction to a readable string."""
    try:
        if hasattr(value, "numerator") and hasattr(value, "denominator"):
            num, den = int(value.numerator), int(value.denominator)
        elif isinstance(value, tuple) and len(value) == 2:
            num, den = int(value[0]), int(value[1])
        else:
            return str(value)
        if den == 0:
            return None
        if num % den == 0:
            return str(num // den)
        return f"{num}/{den}"
    except Exception:
        return str(value)


def _safe_str(value: Any) -> Optional[str]:
    if value is None:
        return None
    try:
        return str(value).strip() or None
    except Exception:
        return None


def analyze_with_pillow(file_path: str) -> dict:
    """Extract metadata from JPG/TIFF using Pillow."""
    from PIL import Image
    from PIL.ExifTags import TAGS

    result: dict = {
        "width_px": None,
        "height_px": None,
        "color_mode_raw": None,
        "manufacturer": None,
        "camera_model": None,
        "exposure": None,
        "diaphragm_aperture": None,
        "iso_sensitivity": None,
        "lens_optical": None,
        "analyzed_at_exif": None,
        "raw_exif": {},
    }

    with Image.open(file_path) as img:
        result["width_px"] = img.width
        result["height_px"] = img.height
        result["color_mode_raw"] = img.mode

        raw_exif = img._getexif() or {}
        # Build a human-readable dict of all tags
        readable: dict = {}
        for tag_id, val in raw_exif.items():
            tag_name = TAGS.get(tag_id, str(tag_id))
            try:
                readable[tag_name] = _safe_str(val)
            except Exception:
                pass

        result["raw_exif"] = readable
        result["manufacturer"] = _safe_str(raw_exif.get(271))
        result["camera_model"] = _safe_str(raw_exif.get(272))
        result["exposure"] = _fraction_to_str(raw_exif.get(33434))
        result["diaphragm_aperture"] = _fraction_to_str(raw_exif.get(33437))
        iso = raw_exif.get(34855)
        result["iso_sensitivity"] = _safe_str(iso)
        focal = raw_exif.get(37386)
        result["lens_optical"] = _fraction_to_str(focal)
        lens_model = raw_exif.get(42036)
        if lens_model:
            existing = result["lens_optical"] or ""
            result["lens_optical"] = f"{existing} {lens_model}".strip()
        result["analyzed_at_exif"] = _safe_str(raw_exif.get(36867) or raw_exif.get(306))

    return result


def analyze_with_exiftool(file_path: str) -> dict:
    """
    Extract metadata from any file (including CR3) via ExifTool CLI.
    Requires ExifTool to be installed and on PATH.
    """
    proc = subprocess.run(
        ["exiftool", "-j", "-n", file_path],
        capture_output=True, text=True, timeout=30,
    )
    if proc.returncode != 0:
        raise RuntimeError(f"ExifTool error: {proc.stderr.strip()}")

    data = json.loads(proc.stdout)[0]

    def _get(*keys: str) -> Optional[str]:
        for k in keys:
            if k in data:
                return _safe_str(data[k])
        return None

    return {
        "width_px": data.get("ImageWidth") or data.get("ExifImageWidth"),
        "height_px": data.get("ImageHeight") or data.get("ExifImageHeight"),
        "color_mode_raw": _get("ColorSpace", "PhotometricInterpretation"),
        "manufacturer": _get("Make"),
        "camera_model": _get("Model"),
        "exposure": _get("ExposureTime", "ShutterSpeedValue"),
        "diaphragm_aperture": _get("FNumber", "Aperture"),
        "iso_sensitivity": _get("ISO"),
        "lens_optical": _get("LensModel", "Lens", "FocalLength"),
        "analyzed_at_exif": _get("DateTimeOriginal", "CreateDate"),
        "raw_exif": {k: _safe_str(v) for k, v in data.items()},
    }


def analyze(file_path: str) -> dict:
    """
    Main entry point. Chooses the right extractor based on file extension.
    Always returns a dict; errors are captured in 'error' key.
    """
    if not os.path.exists(file_path):
        return {"error": f"Archivo no encontrado: {file_path}"}

    ext = os.path.splitext(file_path)[1].lower()

    try:
        if ext in (".jpg", ".jpeg", ".tif", ".tiff"):
            data = analyze_with_pillow(file_path)
        elif ext in (".cr3", ".cr2", ".nef", ".arw", ".raf"):
            # Raw formats require ExifTool
            data = analyze_with_exiftool(file_path)
        else:
            # Try Pillow first, fall back to ExifTool
            try:
                data = analyze_with_pillow(file_path)
            except Exception:
                data = analyze_with_exiftool(file_path)

        data["error"] = None
        data["provider"] = PROVIDER_NAME
        data["provider_version"] = PROVIDER_VERSION
        return data

    except FileNotFoundError:
        return {
            "error": "ExifTool no está instalado. Instálalo en PATH para procesar archivos RAW.",
            "provider": PROVIDER_NAME,
            "provider_version": PROVIDER_VERSION,
        }
    except Exception as exc:
        return {
            "error": str(exc),
            "provider": PROVIDER_NAME,
            "provider_version": PROVIDER_VERSION,
        }
