"""
Base compartida para analizadores de visión usando Groq API.
Convierte la imagen a base64 y llama al modelo vision de Groq.
"""

import base64
import json
import os
import re


GROQ_BASE_URL = "https://api.groq.com/openai/v1"
GROQ_VISION_MODEL = "meta-llama/llama-4-scout-17b-16e-instruct"


def _image_to_base64(file_path: str) -> tuple[str, str]:
    ext = os.path.splitext(file_path)[1].lower()
    mime = {
        ".jpg": "image/jpeg", ".jpeg": "image/jpeg",
        ".png": "image/png", ".tif": "image/tiff", ".tiff": "image/tiff",
    }.get(ext, "image/jpeg")
    with open(file_path, "rb") as f:
        data = base64.b64encode(f.read()).decode("utf-8")
    return data, mime


def _parse_json_response(text: str) -> dict:
    """Extrae JSON del texto aunque venga dentro de markdown code blocks."""
    text = text.strip()
    match = re.search(r"```(?:json)?\s*([\s\S]+?)```", text)
    if match:
        text = match.group(1).strip()
    return json.loads(text)


def call_groq_vision(api_key: str, system_prompt: str, user_prompt: str, file_path: str) -> str:
    from openai import OpenAI

    client = OpenAI(api_key=api_key, base_url=GROQ_BASE_URL)
    b64, mime = _image_to_base64(file_path)

    response = client.chat.completions.create(
        model=GROQ_VISION_MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {
                "role": "user",
                "content": [
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:{mime};base64,{b64}"},
                    },
                    {"type": "text", "text": user_prompt},
                ],
            },
        ],
        temperature=0.1,
        max_tokens=512,
    )
    return response.choices[0].message.content
