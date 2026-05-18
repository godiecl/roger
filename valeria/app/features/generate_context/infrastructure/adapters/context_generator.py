import time
from typing import Optional

import structlog

from app.features.generate_context.domain.context import ImageContext
from app.features.generate_context.domain.context_port import IContextGenerator
from app.infrastructure.ai.llm.llm_factory import create_llm_provider

logger = structlog.get_logger()

_SYSTEM_PROMPT = """Eres un historiador experto en patrimonio fotográfico latinoamericano del siglo XX,
con conocimiento profundo de la vida y obra de Robert Gerstmann (1886-1964) y el contexto
histórico de Chile y Sudamérica. Tu rol es proporcionar contexto histórico riguroso y educativo
sobre fotografías de archivo, distinguiendo claramente entre hechos verificados e interpretaciones."""

_USER_PROMPT_TEMPLATE = """Genera un párrafo de contexto histórico para esta fotografía de archivo:

Título: {title}
Descripción: {description}
Año aproximado: {year}
Ubicación: {location}

El párrafo debe:
- Situar la fotografía en su contexto histórico (período, lugar, relevancia)
- Mencionar hechos históricos del período si son pertinentes
- Ser informativo, preciso y entre 100 y 180 palabras
- Usar tono académico pero accesible
- Si hay incertidumbre sobre la fecha o lugar, indicarlo explícitamente

Responde SOLO con el párrafo de texto, sin títulos, sin comillas, sin texto adicional."""


class ContextGenerator(IContextGenerator):
    async def generate(
        self,
        image_id: int,
        title: Optional[str],
        description: Optional[str],
        year: Optional[int],
        location: Optional[str],
    ) -> ImageContext:
        llm = create_llm_provider()
        provider_name = type(llm).__name__.lower().replace("provider", "").replace("client", "")

        prompt = _USER_PROMPT_TEMPLATE.format(
            title=title or "Sin título",
            description=description or "Sin descripción disponible",
            year=str(year) if year else "Desconocido",
            location=location or "Desconocida",
        )

        start = time.time()
        try:
            text = await llm.generate(
                system_prompt=_SYSTEM_PROMPT,
                user_prompt=prompt,
                max_tokens=300,
                temperature=0.7,
            )
        except Exception as e:
            logger.error("context_generation_failed", image_id=image_id, error=str(e))
            raise

        elapsed_ms = int((time.time() - start) * 1000)

        return ImageContext(
            image_id=image_id,
            text=text.strip(),
            provider=provider_name,
            generation_time_ms=elapsed_ms,
        )
