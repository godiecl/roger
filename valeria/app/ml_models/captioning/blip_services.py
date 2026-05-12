import os
import torch
from PIL import Image
from transformers import BlipProcessor, BlipForConditionalGeneration


class BlipService:
    def __init__(self):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model_id = "Salesforce/blip-image-captioning-base"

        self.processor = BlipProcessor.from_pretrained(self.model_id)
        self.model = BlipForConditionalGeneration.from_pretrained(
            self.model_id,
            torch_dtype=torch.float16 if self.device == "cuda" else torch.float32
        ).to(self.device)

        self.model.eval()

    def describe(self, image_path: str):
        if not os.path.exists(image_path):
            return {
                "error": f"No existe la imagen: {image_path}"
            }

        image = Image.open(image_path).convert("RGB")

        inputs = self.processor(
            image,
            return_tensors="pt"
        ).to(self.device)

        with torch.no_grad():
            output = self.model.generate(
                **inputs,
                max_new_tokens=80
            )

        caption = self.processor.decode(
            output[0],
            skip_special_tokens=True
        ).strip()

        return {
            "image_name": os.path.basename(image_path),
            "caption_en": caption,
            "model": self.model_id
        }