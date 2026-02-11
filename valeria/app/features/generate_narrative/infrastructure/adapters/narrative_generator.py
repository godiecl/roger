"""
Narrative generator service using LLMs and RAG
"""
import time
from typing import Optional, List
import structlog

from app.features.generate_narrative.domain.narrative_port import NarrativeGeneratorPort
from app.features.generate_narrative.domain.narrative import Narrative
from app.features.generate_narrative.domain.trazabilidad import Trazabilidad, Source, SourceType
from app.features.view_images.domain.image import Image
from app.features.view_images.infrastructure.adapters.image_repository import ImageRepository
from app.infrastructure.ai.llm.openai_client import OpenAIClient
from app.infrastructure.rag.vector_stores.chroma_store import ChromaVectorStore
# from app.infrastructure.rag.retrievers.retriever import Retriever  # TODO: Implement Retriever class
from sqlalchemy.ext.asyncio import AsyncSession

logger = structlog.get_logger()


class NarrativeGenerator(NarrativeGeneratorPort):
    """
    Narrative generator service.
    Uses RAG to retrieve historical context and LLM to generate narratives.
    """

    def __init__(
        self,
        db_session: AsyncSession,
        llm_client: OpenAIClient,
        vector_store: ChromaVectorStore = None
    ):
        """
        Initialize the narrative generator.

        Args:
            db_session: Database session
            llm_client: LLM client for text generation
            vector_store: Vector store for RAG
        """
        self.db_session = db_session
        self.llm_client = llm_client
        self.vector_store = vector_store
        self.image_repository = ImageRepository(db_session)

        # TODO: Implement Retriever class for RAG functionality
        # if vector_store:
        #     self.retriever = Retriever(vector_store)
        # else:
        #     self.retriever = None
        self.retriever = None

    async def generate(
        self,
        image_id: int,
        prompt: Optional[str] = None,
        language: str = "es",
        user_id: Optional[int] = None
    ) -> Narrative:
        """
        Generate a narrative for an image using RAG and LLM.
        """
        start_time = time.time()

        # Get image details
        image = await self.image_repository.get_by_id(image_id)
        if not image:
            raise ValueError(f"Image {image_id} not found")

        logger.info(
            "Generating narrative for image",
            image_id=image_id,
            title=image.title,
            language=language
        )

        # Retrieve historical context using RAG
        context_docs = await self._retrieve_context(image)

        # Build sources from retrieved documents
        sources = self._build_sources(context_docs)

        # Determine primary source type
        primary_source_type = self._determine_primary_source_type(sources)

        # Calculate confidence score
        confidence_score = self._calculate_confidence(sources, context_docs)

        # Generate narrative text using LLM
        narrative_text = await self._generate_text(
            image=image,
            context_docs=context_docs,
            prompt=prompt,
            language=language
        )

        # Create trazabilidad
        trazabilidad = Trazabilidad(
            sources=sources,
            primary_source_type=primary_source_type,
            confidence_score=confidence_score
        )

        # Calculate generation time
        generation_time_ms = int((time.time() - start_time) * 1000)

        # Create narrative entity
        narrative = Narrative(
            image_id=image_id,
            text=narrative_text,
            trazabilidad=trazabilidad,
            user_id=user_id,
            prompt=prompt,
            language=language,
            model_used=self.llm_client.model,
            generation_time_ms=generation_time_ms
        )

        logger.info(
            "Narrative generated",
            image_id=image_id,
            confidence=confidence_score,
            primary_source_type=primary_source_type.value,
            generation_time_ms=generation_time_ms
        )

        return narrative

    async def regenerate(
        self,
        narrative_id: int,
        prompt: Optional[str] = None
    ) -> Narrative:
        """
        Regenerate is handled by the use case.
        This method is not used directly.
        """
        raise NotImplementedError("Use GenerateNarrativeUseCase.regenerate instead")

    async def _retrieve_context(self, image: Image) -> List[dict]:
        """
        Retrieve relevant historical context for the image using RAG.
        """
        if not self.retriever:
            logger.warning("No retriever available, generating without RAG context")
            return []

        try:
            # Build query from image metadata
            query_parts = []
            if image.title:
                query_parts.append(image.title)
            if image.location:
                query_parts.append(image.location)
            if image.year:
                query_parts.append(str(image.year))
            if image.description:
                query_parts.append(image.description)

            query = " ".join(query_parts)

            # Retrieve from historical documents
            docs = await self.retriever.retrieve(
                query=query,
                collection_name="historical_docs",
                k=5
            )

            logger.info("Retrieved context documents", count=len(docs))
            return docs

        except Exception as e:
            logger.error("Failed to retrieve context", error=str(e))
            return []

    def _build_sources(self, context_docs: List[dict]) -> List[Source]:
        """Build Source objects from retrieved documents."""
        sources = []

        if not context_docs:
            # No RAG context available - all will be AI-generated
            sources.append(
                Source(
                    text="Generado por IA basado en metadatos de la imagen",
                    source_type=SourceType.VEROSIMIL,
                    reference="AI-generated"
                )
            )
            return sources

        for doc in context_docs:
            metadata = doc.get("metadata", {})
            source_type_str = metadata.get("source_type", "verosímil")

            # Determine source type
            if source_type_str == "veraz" or metadata.get("verified", False):
                source_type = SourceType.VERAZ
            else:
                source_type = SourceType.VEROSIMIL

            source = Source(
                text=doc.get("text", "")[:500],  # Truncate for storage
                source_type=source_type,
                reference=metadata.get("reference", metadata.get("document_id")),
                relevance_score=doc.get("score")
            )
            sources.append(source)

        return sources

    def _determine_primary_source_type(self, sources: List[Source]) -> SourceType:
        """Determine the primary source type based on sources."""
        if not sources:
            return SourceType.VEROSIMIL

        verified_count = sum(1 for s in sources if s.is_verified())
        total_count = len(sources)

        # If majority are verified, primary type is VERAZ
        if verified_count / total_count >= 0.5:
            return SourceType.VERAZ
        else:
            return SourceType.VEROSIMIL

    def _calculate_confidence(
        self,
        sources: List[Source],
        context_docs: List[dict]
    ) -> float:
        """Calculate confidence score based on sources and context."""
        if not context_docs:
            # No RAG context - lower confidence
            return 0.3

        # Base confidence on number and quality of sources
        verified_count = sum(1 for s in sources if s.is_verified())
        total_count = len(sources)

        # Average relevance score
        avg_relevance = sum(
            s.relevance_score for s in sources if s.relevance_score
        ) / max(len([s for s in sources if s.relevance_score]), 1)

        # Calculate confidence
        confidence = 0.5  # Base confidence
        confidence += (verified_count / total_count) * 0.3  # Up to +0.3 for verified sources
        confidence += min(avg_relevance, 0.2)  # Up to +0.2 for relevance

        return min(confidence, 1.0)

    async def _generate_text(
        self,
        image: Image,
        context_docs: List[dict],
        prompt: Optional[str],
        language: str
    ) -> str:
        """
        Generate narrative text using LLM.
        """
        # Build context from retrieved documents
        context_text = ""
        if context_docs:
            context_text = "\n\n".join([
                f"Fuente: {doc.get('text', '')}"
                for doc in context_docs[:3]  # Top 3 most relevant
            ])

        # Build system prompt
        system_prompt = self._build_system_prompt(language)

        # Build user prompt
        user_prompt = self._build_user_prompt(image, context_text, prompt, language)

        try:
            # Generate using LLM
            response = await self.llm_client.generate(
                prompt=user_prompt,
                system_prompt=system_prompt,
                max_tokens=1000,
                temperature=0.7
            )

            return response.strip()

        except Exception as e:
            logger.error("Failed to generate narrative text", error=str(e))
            # Fallback to basic description
            return self._generate_fallback_narrative(image, language)

    def _build_system_prompt(self, language: str) -> str:
        """Build system prompt for the LLM."""
        if language == "es":
            return """Eres un experto historiador especializado en fotografía histórica chilena
y en la obra de Robert Gerstmann. Tu tarea es generar narrativas contextuales
sobre imágenes históricas, proporcionando información precisa y enriquecedora.

Cuando se te proporcione contexto histórico verificado, úsalo como base principal.
Si el contexto es limitado, genera una narrativa plausible basada en tu conocimiento
histórico, pero mantén un tono apropiadamente cauteloso.

La narrativa debe ser:
- Informativa y educativa
- Históricamente precisa (cuando hay fuentes verificadas)
- Contextualizada en la época y lugar
- Escrita en un tono académico pero accesible
- De 2-3 párrafos de longitud"""
        elif language == "en":
            return """You are an expert historian specialized in Chilean historical photography
and the work of Robert Gerstmann. Your task is to generate contextual narratives
about historical images, providing accurate and enriching information.

When provided with verified historical context, use it as the primary basis.
If context is limited, generate a plausible narrative based on your historical
knowledge, but maintain an appropriately cautious tone.

The narrative should be:
- Informative and educational
- Historically accurate (when verified sources are available)
- Contextualized in time and place
- Written in an academic yet accessible tone
- 2-3 paragraphs in length"""
        else:
            return "Generate a historical narrative about the image."

    def _build_user_prompt(
        self,
        image: Image,
        context: str,
        custom_prompt: Optional[str],
        language: str
    ) -> str:
        """Build user prompt with image details and context."""
        parts = []

        if language == "es":
            parts.append("Genera una narrativa histórica sobre la siguiente imagen:\n")
            parts.append(f"Título: {image.title}")
            if image.year:
                parts.append(f"Año: {image.year}")
            if image.location:
                parts.append(f"Ubicación: {image.location}")
            if image.description:
                parts.append(f"Descripción: {image.description}")
            if image.author:
                parts.append(f"Autor: {image.author}")

            if context:
                parts.append(f"\nContexto histórico disponible:\n{context}")

            if custom_prompt:
                parts.append(f"\nEnfoque específico solicitado: {custom_prompt}")

            parts.append("\nGenera la narrativa histórica:")
        else:
            parts.append("Generate a historical narrative about the following image:\n")
            parts.append(f"Title: {image.title}")
            if image.year:
                parts.append(f"Year: {image.year}")
            if image.location:
                parts.append(f"Location: {image.location}")
            if image.description:
                parts.append(f"Description: {image.description}")
            if image.author:
                parts.append(f"Author: {image.author}")

            if context:
                parts.append(f"\nAvailable historical context:\n{context}")

            if custom_prompt:
                parts.append(f"\nSpecific focus requested: {custom_prompt}")

            parts.append("\nGenerate the historical narrative:")

        return "\n".join(parts)

    def _generate_fallback_narrative(self, image: Image, language: str) -> str:
        """Generate a basic fallback narrative when LLM is unavailable."""
        if language == "es":
            description = image.description if image.description else 'Esta imagen forma parte de la colección histórica y representa un valioso registro visual del patrimonio cultural chileno.'
            return f"""Esta fotografía titulada "{image.title}" fue capturada por {image.author}
{f'en {image.year}' if image.year else 'en una fecha no especificada'}
{f'en {image.location}' if image.location else ''}.

{description}

Esta narrativa fue generada automáticamente. Para obtener una narrativa más detallada
y contextualizada, configure la API de OpenAI."""
        else:
            description = image.description if image.description else 'This image is part of the historical collection and represents a valuable visual record of Chilean cultural heritage.'
            return f"""This photograph titled "{image.title}" was captured by {image.author}
{f'in {image.year}' if image.year else 'at an unspecified date'}
{f'in {image.location}' if image.location else ''}.

{description}

This narrative was automatically generated. For a more detailed and contextualized
narrative, configure the OpenAI API."""
