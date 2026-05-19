"""
FastAPI routes for narratives
"""
import asyncio
import hashlib
import time
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, Request, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select as sa_select
from typing import Optional, List

from app.features.authenticate.domain.role import Role
from app.features.authenticate.infrastructure.adapters.user_repository import UserRepository
from app.features.authenticate.interfaces.api.dependencies import get_current_user_id
from app.features.generate_narrative.interfaces.api.schemas import (
    NarrativeResponse,
    NarrativeListResponse,
    GenerateNarrativeRequest,
    RegenerateNarrativeRequest,
    ApproveNarrativeRequest,
    TrazabilidadResponse,
    SourceResponse,
    LLMCompareRequest,
    LLMCompareResponse,
    LLMProviderResult,
)
from app.features.generate_narrative.application.generate_narrative_usecase import (
    GenerateNarrativeUseCase
)
from app.features.generate_narrative.infrastructure.adapters.narrative_repository import (
    NarrativeRepository
)
from app.features.generate_narrative.infrastructure.adapters.narrative_generator import (
    NarrativeGenerator
)
from app.infrastructure.database.session import get_db
from app.infrastructure.ai.llm.openai_client import OpenAIClient
from app.infrastructure.rag.vector_stores.chroma_store import ChromaVectorStore
from app.config.settings import settings


router = APIRouter(prefix="/narratives", tags=["Narratives"])


async def _require_curator_or_admin(
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> int:
    user_repo = UserRepository(db)
    user = await user_repo.get_by_id(user_id)
    if not user or user.role not in (Role.CURADOR, Role.ADMINISTRADOR):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo curadores y administradores pueden gestionar narrativas.",
        )
    return user_id


def get_llm_client() -> OpenAIClient:
    """Get LLM client instance."""
    return OpenAIClient(
        api_key=settings.openai_api_key,
        model=settings.openai_model
    )


def get_chroma_store() -> ChromaVectorStore:
    """Get ChromaDB vector store instance."""
    try:
        return ChromaVectorStore(persist_directory=settings.chroma_persist_directory)
    except Exception:
        return None


@router.post("", response_model=NarrativeResponse, status_code=status.HTTP_201_CREATED)
async def generate_narrative(
    request: GenerateNarrativeRequest,
    user_id: int = Depends(_require_curator_or_admin),
    db: AsyncSession = Depends(get_db)
):
    """
    Generate a new narrative for an image using AI. Requires curator or admin role.
    """
    try:
        llm_client = get_llm_client()
        vector_store = get_chroma_store()
        generator = NarrativeGenerator(db, llm_client, vector_store)
        repository = NarrativeRepository(db)
        usecase = GenerateNarrativeUseCase(generator, repository)

        narrative = await usecase.execute(
            image_id=request.image_id,
            prompt=request.prompt,
            language=request.language,
            user_id=user_id,
        )

        # Convert to response
        return _narrative_to_response(narrative)

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate narrative: {str(e)}"
        )


_GROQ_BASE = "https://api.groq.com/openai/v1"
_COMPARE_ROLES = (Role.CURADOR, Role.ADMINISTRADOR, Role.INVESTIGADOR)
_DEFAULT_SYSTEM = (
    "Eres un historiador especialista en fotografía patrimonial chilena del siglo XX. "
    "Genera una narrativa descriptiva, precisa y contextualizada para la siguiente fotografía del archivo. "
    "Distingue entre lo verificable (VERAZ) y lo interpretativo (VEROSÍMIL). "
    "Responde en español con un párrafo de 3 a 5 oraciones."
)


def _build_available_providers() -> List[tuple]:
    from app.infrastructure.ai.llm.openai_compatible_adapter import OpenAICompatibleAdapter
    from app.infrastructure.ai.llm.anthropic_adapter import AnthropicAdapter

    providers: List[tuple] = []
    if settings.groq_api_key:
        providers.append((
            OpenAICompatibleAdapter(
                api_key=settings.groq_api_key,
                model=settings.groq_model,
                max_tokens=settings.llm_max_tokens,
                temperature=settings.llm_temperature,
                base_url=_GROQ_BASE,
                name=f"groq/{settings.groq_model}",
            ),
            f"groq/{settings.groq_model}",
        ))
    if settings.openai_api_key:
        providers.append((
            OpenAICompatibleAdapter(
                api_key=settings.openai_api_key,
                model=settings.openai_model,
                max_tokens=settings.llm_max_tokens,
                temperature=settings.llm_temperature,
                name=f"openai/{settings.openai_model}",
            ),
            f"openai/{settings.openai_model}",
        ))
    if settings.anthropic_api_key:
        providers.append((
            AnthropicAdapter(
                api_key=settings.anthropic_api_key,
                model=settings.anthropic_model or "claude-3-5-sonnet-20241022",
                max_tokens=settings.llm_max_tokens,
                temperature=settings.llm_temperature,
            ),
            f"anthropic/{settings.anthropic_model or 'claude-3-5-sonnet-20241022'}",
        ))
    return providers


async def _call_provider(provider_instance, display_name: str, messages: list) -> LLMProviderResult:
    t0 = time.monotonic()
    try:
        response = await provider_instance.complete(messages)
        return LLMProviderResult(
            provider=display_name,
            response=response,
            time_ms=int((time.monotonic() - t0) * 1000),
            error=None,
        )
    except Exception as exc:
        return LLMProviderResult(
            provider=display_name,
            response="",
            time_ms=int((time.monotonic() - t0) * 1000),
            error=str(exc),
        )


@router.post("/compare", response_model=LLMCompareResponse, summary="Comparar respuestas de múltiples LLMs")
async def compare_llms(
    body: LLMCompareRequest,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """
    Envía el mismo prompt a todos los LLMs configurados en paralelo y retorna
    sus respuestas lado a lado. Útil para evaluar la calidad de distintos modelos
    sobre el mismo material fotográfico. Requiere rol curador, administrador o investigador.
    """
    from app.features.archive.infrastructure.persistence.archive_model import PhotographModel
    from app.features.detect_objects.infrastructure.persistence.detection_model import ObjectDetectionModel

    user_repo = UserRepository(db)
    user = await user_repo.get_by_id(user_id)
    if not user or user.role not in _COMPARE_ROLES:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Acceso no autorizado.")

    ph_result = await db.execute(sa_select(PhotographModel).where(PhotographModel.id == body.photograph_id))
    photograph = ph_result.scalar_one_or_none()
    if not photograph:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Fotografía no encontrada.")

    det_result = await db.execute(
        sa_select(ObjectDetectionModel)
        .where(ObjectDetectionModel.photograph_id == body.photograph_id)
        .order_by(ObjectDetectionModel.created_at.desc())
        .limit(1)
    )
    detection = det_result.scalar_one_or_none()

    # Build user_prompt from photograph metadata when not provided
    if body.user_prompt:
        user_prompt = body.user_prompt
    else:
        parts: List[str] = []
        if getattr(photograph, 'reference_code', None):
            parts.append(f"Código de referencia: {photograph.reference_code}")
        if photograph.identifier:
            parts.append(f"Identificador: {photograph.identifier}")
        if photograph.internal_cronology:
            parts.append(f"Cronología: {photograph.internal_cronology}")
        if getattr(photograph, 'scope_content', None):
            parts.append(f"Alcance y contenido: {photograph.scope_content}")
        if detection and detection.scene_description:
            parts.append(f"Descripción de escena (YOLO/IA): {detection.scene_description}")
        user_prompt = "\n".join(parts) if parts else f"Fotografía ID {body.photograph_id} del archivo histórico."

    system_prompt = body.system_prompt or _DEFAULT_SYSTEM
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user",   "content": user_prompt},
    ]

    providers = _build_available_providers()
    if not providers:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="No hay proveedores LLM configurados. Revisa las variables GROQ_API_KEY / OPENAI_API_KEY / ANTHROPIC_API_KEY.",
        )

    tasks = [_call_provider(inst, name, messages) for inst, name in providers]
    results = await asyncio.gather(*tasks)

    return LLMCompareResponse(
        photograph_id=body.photograph_id,
        system_prompt=system_prompt,
        user_prompt=user_prompt,
        results=list(results),
        computed_at=datetime.now(timezone.utc).isoformat(),
    )


@router.get("/{narrative_id}", response_model=NarrativeResponse)
async def get_narrative(
    narrative_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Get a specific narrative by ID.
    """
    repository = NarrativeRepository(db)
    narrative = await repository.get_by_id(narrative_id)

    if not narrative:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Narrative {narrative_id} not found"
        )

    return _narrative_to_response(narrative)


@router.get("/image/{image_id}", response_model=NarrativeListResponse)
async def get_narratives_for_image(
    image_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Get approved narratives for a specific image (public endpoint).
    """
    repository = NarrativeRepository(db)
    narratives = await repository.get_by_image_id(image_id, only_approved=True)

    return NarrativeListResponse(
        total=len(narratives),
        skip=0,
        limit=len(narratives),
        narratives=[_narrative_to_response(n) for n in narratives]
    )


@router.get("", response_model=NarrativeListResponse)
async def list_narratives(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    only_approved: bool = Query(False),
    db: AsyncSession = Depends(get_db)
):
    """
    List all narratives with pagination.

    - **skip**: Number of narratives to skip
    - **limit**: Maximum number of narratives to return
    - **only_approved**: Only return approved narratives
    """
    repository = NarrativeRepository(db)
    narratives = await repository.list(skip, limit, only_approved)

    return NarrativeListResponse(
        total=len(narratives),  # TODO: Get actual total count
        skip=skip,
        limit=limit,
        narratives=[_narrative_to_response(n) for n in narratives]
    )


@router.post("/{narrative_id}/regenerate", response_model=NarrativeResponse)
async def regenerate_narrative(
    narrative_id: int,
    request: RegenerateNarrativeRequest,
    _: int = Depends(_require_curator_or_admin),
    db: AsyncSession = Depends(get_db)
):
    """
    Regenerate an existing narrative with a new prompt. Requires curator or admin role.
    """
    try:
        # Initialize services
        llm_client = get_llm_client()
        vector_store = get_chroma_store()
        generator = NarrativeGenerator(db, llm_client, vector_store)
        repository = NarrativeRepository(db)
        usecase = GenerateNarrativeUseCase(generator, repository)

        # Regenerate
        narrative = await usecase.regenerate(
            narrative_id=narrative_id,
            prompt=request.prompt
        )

        return _narrative_to_response(narrative)

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to regenerate narrative: {str(e)}"
        )


@router.post("/{narrative_id}/approve", response_model=NarrativeResponse)
async def approve_narrative(
    narrative_id: int,
    user_id: int = Depends(_require_curator_or_admin),
    db: AsyncSession = Depends(get_db)
):
    """
    Approve a narrative. Requires curator or admin role.
    """
    try:
        repository = NarrativeRepository(db)
        generator = NarrativeGenerator(db, get_llm_client(), get_chroma_store())
        usecase = GenerateNarrativeUseCase(generator, repository)

        narrative = await usecase.approve_narrative(
            narrative_id=narrative_id,
            approved_by=user_id,
        )

        return _narrative_to_response(narrative)

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@router.post("/{narrative_id}/unapprove", response_model=NarrativeResponse)
async def unapprove_narrative(
    narrative_id: int,
    _: int = Depends(_require_curator_or_admin),
    db: AsyncSession = Depends(get_db)
):
    """
    Unapprove a narrative. Requires curator or admin role.
    """
    try:
        repository = NarrativeRepository(db)
        generator = NarrativeGenerator(db, get_llm_client(), get_chroma_store())
        usecase = GenerateNarrativeUseCase(generator, repository)

        narrative = await usecase.unapprove_narrative(narrative_id)

        return _narrative_to_response(narrative)

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@router.delete("/{narrative_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_narrative(
    narrative_id: int,
    _: int = Depends(_require_curator_or_admin),
    db: AsyncSession = Depends(get_db)
):
    """
    Delete a narrative. Requires curator or admin role.
    """
    repository = NarrativeRepository(db)
    success = await repository.delete(narrative_id)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Narrative {narrative_id} not found"
        )

    return None


@router.post("/{narrative_id}/like")
async def toggle_narrative_like(
    narrative_id: int,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """Toggle like en una narrativa. Limitado a 1 por IP."""
    from sqlalchemy import select
    from sqlalchemy.exc import IntegrityError
    from app.features.generate_context.infrastructure.persistence.like_model import ContentLikeModel
    from app.features.generate_narrative.infrastructure.persistence.narrative_model import NarrativeModel

    ip = request.client.host if request.client else "unknown"
    ip_hash = hashlib.sha256(ip.encode()).hexdigest()

    nm_result = await db.execute(select(NarrativeModel).where(NarrativeModel.id == narrative_id))
    nm = nm_result.scalar_one_or_none()
    if not nm:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Narrative not found")

    like_result = await db.execute(
        select(ContentLikeModel).where(
            ContentLikeModel.content_type == "narrative",
            ContentLikeModel.content_id == narrative_id,
            ContentLikeModel.ip_hash == ip_hash,
        )
    )
    existing = like_result.scalar_one_or_none()

    if existing:
        await db.delete(existing)
        nm.like_count = max(0, nm.like_count - 1)
        await db.flush()
        return {"liked": False, "like_count": nm.like_count}

    db.add(ContentLikeModel(content_type="narrative", content_id=narrative_id, ip_hash=ip_hash))
    nm.like_count += 1
    try:
        await db.flush()
    except IntegrityError:
        await db.rollback()
    return {"liked": True, "like_count": nm.like_count}


@router.post("/{narrative_id}/report", status_code=status.HTTP_204_NO_CONTENT)
async def report_narrative(
    narrative_id: int,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """Reporta una narrativa. One-way: 409 si ya fue reportado desde esta IP."""
    from sqlalchemy import select
    from sqlalchemy.exc import IntegrityError
    from app.features.generate_context.infrastructure.persistence.report_model import ContentReportModel
    from app.features.generate_narrative.infrastructure.persistence.narrative_model import NarrativeModel

    ip = request.client.host if request.client else "unknown"
    ip_hash = hashlib.sha256(ip.encode()).hexdigest()

    nm_result = await db.execute(select(NarrativeModel).where(NarrativeModel.id == narrative_id))
    nm = nm_result.scalar_one_or_none()
    if not nm:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Narrative not found")

    db.add(ContentReportModel(content_type="narrative", content_id=narrative_id, ip_hash=ip_hash))
    try:
        await db.flush()
        nm.report_count += 1
        await db.flush()
    except IntegrityError:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Ya reportaste esta narrativa.")


def _narrative_to_response(narrative) -> NarrativeResponse:
    """Convert domain narrative to response schema."""
    return NarrativeResponse(
        id=narrative.id,
        image_id=narrative.image_id,
        text=narrative.text,
        trazabilidad=TrazabilidadResponse(
            sources=[
                SourceResponse(
                    text=s.text,
                    source_type=s.source_type.value,
                    reference=s.reference,
                    relevance_score=s.relevance_score
                )
                for s in narrative.trazabilidad.sources
            ],
            primary_source_type=narrative.trazabilidad.primary_source_type.value,
            confidence_score=narrative.trazabilidad.confidence_score,
            verified_sources_count=len(narrative.trazabilidad.get_verified_sources()),
            plausible_sources_count=len(narrative.trazabilidad.get_plausible_sources())
        ),
        user_id=narrative.user_id,
        prompt=narrative.prompt,
        language=narrative.language,
        model_used=narrative.model_used,
        generation_time_ms=narrative.generation_time_ms,
        is_approved=narrative.is_approved,
        approved_by=narrative.approved_by,
        approved_at=narrative.approved_at,
        is_verified=narrative.is_verified(),
        confidence_level=narrative.get_confidence_level(),
        created_at=narrative.created_at,
        updated_at=narrative.updated_at
    )
