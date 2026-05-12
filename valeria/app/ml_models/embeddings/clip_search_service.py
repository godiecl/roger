import os
import torch
import open_clip
import faiss
import numpy as np
from PIL import Image


class ClipSearchService:
    def __init__(self, image_dir: str):
        self.image_dir = image_dir
        self.device = "cuda" if torch.cuda.is_available() else "cpu"

        self.model, _, self.preprocess = open_clip.create_model_and_transforms(
            "ViT-B-32",
            pretrained="laion2b_s34b_b79k"
        )

        self.tokenizer = open_clip.get_tokenizer("ViT-B-32")
        self.model = self.model.to(self.device)
        self.model.eval()

        self.valid_paths = []
        self.image_embeddings = []
        self.index = None

        self._build_index()

    def _encode_image(self, image_path: str):
        image = self.preprocess(
            Image.open(image_path).convert("RGB")
        ).unsqueeze(0).to(self.device)

        with torch.no_grad():
            emb = self.model.encode_image(image)
            emb = emb / emb.norm(dim=-1, keepdim=True)

        return emb.cpu().numpy().astype("float32")

    def _encode_text(self, text: str):
        tokens = self.tokenizer([text]).to(self.device)

        with torch.no_grad():
            emb = self.model.encode_text(tokens)
            emb = emb / emb.norm(dim=-1, keepdim=True)

        return emb.cpu().numpy().astype("float32")

    def _build_index(self):
        if not os.path.exists(self.image_dir):
            raise FileNotFoundError(f"No existe image_dir: {self.image_dir}")

        for filename in os.listdir(self.image_dir):
            if not filename.lower().endswith((".jpg", ".jpeg", ".png", ".webp")):
                continue

            image_path = os.path.join(self.image_dir, filename)

            try:
                emb = self._encode_image(image_path)
                self.image_embeddings.append(emb[0])
                self.valid_paths.append(image_path)
            except Exception as e:
                print(f"Error procesando {image_path}: {e}")

        if not self.image_embeddings:
            raise ValueError("No se encontraron imágenes para construir índice CLIP.")

        self.image_embeddings = np.array(self.image_embeddings).astype("float32")

        self.index = faiss.IndexFlatIP(self.image_embeddings.shape[1])
        self.index.add(self.image_embeddings)

        print(f"Índice CLIP creado con {len(self.valid_paths)} imágenes")

    def search(self, query: str, top_k: int = 5):
        if not query:
            return {
                "error": "La query no puede estar vacía."
            }

        query_emb = self._encode_text(query)
        scores, ids = self.index.search(query_emb, top_k)

        results = []

        for score, idx in zip(scores[0], ids[0]):
            image_path = self.valid_paths[idx]

            results.append({
                "image_name": os.path.basename(image_path),
                "image_path": image_path,
                "score": float(score)
            })

        return {
            "query": query,
            "count": len(results),
            "results": results
        }