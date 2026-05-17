"""
FastAPI routes for narratives
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

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
    SourceResponse
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
