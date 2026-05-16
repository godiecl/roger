from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.features.detect_objects.application.detect_objects_usecase import DetectObjectsUseCase
from app.features.detect_objects.domain.detection import Detection
from app.features.detect_objects.infrastructure.adapters.detection_repository import DetectionRepository
from app.features.detect_objects.infrastructure.adapters.vision_analyzer import VisionAnalyzer
from app.features.detect_objects.interfaces.api.schemas import (
    DetectRequest, DetectedObjectResponse, DetectionListResponse, DetectionResponse,
)
from app.infrastructure.database.session import get_db
from app.shared.domain.exceptions import EntityNotFoundError

router = APIRouter(prefix="/detections", tags=["Object Detection"])


def _build_usecase(db: AsyncSession) -> DetectObjectsUseCase:
    return DetectObjectsUseCase(
        analyzer=VisionAnalyzer(),
        repository=DetectionRepository(db),
    )


@router.post("", response_model=DetectionResponse, status_code=status.HTTP_201_CREATED)
async def detect_objects(
    request: DetectRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Analiza una fotografía con IA para detectar objetos, personas y elementos.

    Usa Claude Vision (Anthropic) u OpenAI GPT-4V según las API keys configuradas.
    Si ya existe una detección para la fotografía, la retorna (sin re-analizar).
    Usa force_reanalysis=true para forzar un nuevo análisis.

    Requiere image_path (ruta relativa al STORAGE_PATH) o image_url.
    """
    try:
        usecase = _build_usecase(db)
        detection = await usecase.execute(
            photograph_id=request.photograph_id,
            image_path=request.image_path,
            image_url=request.image_url,
            force_reanalysis=request.force_reanalysis,
        )
        return _to_response(detection)
    except (ValueError, FileNotFoundError) as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/photograph/{photograph_id}", response_model=DetectionResponse)
async def get_detection_for_photograph(
    photograph_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Retorna la detección más reciente para una fotografía."""
    repository = DetectionRepository(db)
    detection = await repository.get_by_photograph(photograph_id)
    if not detection:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No hay detección para la fotografía {photograph_id}",
        )
    return _to_response(detection)


@router.get("/{detection_id}", response_model=DetectionResponse)
async def get_detection(
    detection_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Retorna una detección por su ID."""
    try:
        usecase = _build_usecase(db)
        detection = await usecase.get(detection_id)
        return _to_response(detection)
    except EntityNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.get("", response_model=DetectionListResponse)
async def list_detections(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
):
    """Lista todas las detecciones con paginación."""
    repository = DetectionRepository(db)
    detections = await repository.list(skip, limit)
    return DetectionListResponse(
        total=len(detections),
        skip=skip,
        limit=limit,
        detections=[_to_response(d) for d in detections],
    )


@router.delete("/{detection_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_detection(
    detection_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Elimina una detección y sus objetos asociados."""
    repository = DetectionRepository(db)
    deleted = await repository.delete(detection_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Detección {detection_id} no encontrada",
        )


def _to_response(detection: Detection) -> DetectionResponse:
    return DetectionResponse(
        id=detection.id,
        photograph_id=detection.photograph_id,
        scene_description=detection.scene_description,
        provider=detection.provider,
        detection_time_ms=detection.detection_time_ms,
        status=detection.status.value,
        object_count=detection.object_count(),
        objects=[
            DetectedObjectResponse(
                id=o.id,
                label=o.label,
                category=o.category.value,
                confidence=o.confidence,
                description=o.description,
            )
            for o in detection.objects
        ],
        created_at=detection.created_at,
        updated_at=detection.updated_at,
    )
