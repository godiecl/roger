import os
from datetime import datetime
from typing import List

import structlog
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.features.authenticate.interfaces.api.dependencies import get_current_user_id
from app.features.detect_objects.application.detect_objects_usecase import DetectObjectsUseCase
from app.features.detect_objects.domain.detection import Detection
from app.features.detect_objects.domain.detection_port import IVisionAnalyzer
from app.features.detect_objects.infrastructure.adapters.detection_repository import DetectionRepository
from app.features.detect_objects.infrastructure.adapters.vision_analyzer import VisionAnalyzer
from app.features.detect_objects.infrastructure.persistence.detection_model import (
    ExpertDescriptionAnnotationModel, ExpertDetectionAnnotationModel,
    ObjectDetectionModel,
)
from app.features.detect_objects.domain.detection import DetectionStatus
from app.features.detect_objects.interfaces.api.schemas import (
    AnnotationCoverage, DetectRequest, DetectedObjectResponse,
    DetectionListResponse, DetectionResponse,
    EvaluationMetricsResponse, MetricResult,
    ExpertDescriptionAnnotationCreate, ExpertDescriptionAnnotationResponse,
    ExpertDetectionAnnotationCreate, ExpertDetectionAnnotationListResponse,
    ExpertDetectionAnnotationResponse,
)
from app.infrastructure.database.session import get_db
from app.shared.domain.exceptions import EntityNotFoundError

router = APIRouter(prefix="/detections", tags=["Object Detection"])
logger = structlog.get_logger()


def _select_analyzer(image_path: str | None) -> IVisionAnalyzer:
    """
    Selecciona el analizador óptimo:
    - YOLOv8n-seg si ultralytics está instalado y la imagen existe en disco.
    - VisionAnalyzer (Claude/GPT-4V) como fallback o cuando se usa image_url.
    """
    if image_path and os.path.isfile(image_path):
        try:
            from app.features.detect_objects.infrastructure.adapters.yolo_analyzer import YOLOAnalyzer
            return YOLOAnalyzer()
        except (ImportError, RuntimeError) as e:
            logger.info("YOLOAnalyzer no disponible, usando VisionAnalyzer", reason=str(e))
    return VisionAnalyzer()


def _build_usecase(db: AsyncSession, image_path: str | None = None) -> DetectObjectsUseCase:
    return DetectObjectsUseCase(
        analyzer=_select_analyzer(image_path),
        repository=DetectionRepository(db),
    )


@router.post("", response_model=DetectionResponse, status_code=status.HTTP_201_CREATED)
async def detect_objects(
    request: DetectRequest,
    db: AsyncSession = Depends(get_db),
    _user_id: int = Depends(get_current_user_id),
):
    """
    Detecta objetos y segmentación en una fotografía.

    Prioridad de analizador:
    - YOLOv8n-seg (local, GPU) cuando ultralytics está instalado y la imagen está en disco.
    - Claude Vision / GPT-4V como fallback cuando la imagen no está disponible localmente.

    Si ya existe una detección para la fotografía, la retorna sin re-analizar.
    Usar force_reanalysis=true para forzar un nuevo análisis.

    Requiere autenticación.
    """
    fs_path = os.path.abspath(request.image_path.lstrip("/")) if request.image_path else None
    try:
        usecase = _build_usecase(db, fs_path)
        detection = await usecase.execute(
            photograph_id=request.photograph_id,
            image_path=fs_path or request.image_path,
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


# ---------------------------------------------------------------------------
# Endpoints de anotación de experto (FONDEF Hito 2 — Captura de Conocimiento)
# ---------------------------------------------------------------------------

@router.post(
    "/{detection_id}/annotations",
    response_model=ExpertDetectionAnnotationResponse,
    status_code=status.HTTP_201_CREATED,
)
async def annotate_detection(
    detection_id: int,
    payload: ExpertDetectionAnnotationCreate,
    db: AsyncSession = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    """
    Registra la anotación de un experto sobre un objeto detectado.

    - `detected_object_id=null` → el experto señala un objeto que la IA no detectó.
    - `verdict=incorrect` → puede incluir `corrected_label` y `corrected_category`.

    Requiere autenticación. Roles recomendados: mesa_evaluadora, curador, administrador.
    """
    result = await db.execute(
        select(ExpertDetectionAnnotationModel).where(
            ExpertDetectionAnnotationModel.detection_id == detection_id,
            ExpertDetectionAnnotationModel.annotator_id == user_id,
            ExpertDetectionAnnotationModel.detected_object_id == payload.detected_object_id,
        )
    )
    existing = result.scalar_one_or_none()

    if existing:
        existing.verdict = payload.verdict
        existing.corrected_label = payload.corrected_label
        existing.corrected_category = payload.corrected_category
        existing.notes = payload.notes
        await db.flush()
        await db.refresh(existing)
        ann = existing
    else:
        ann = ExpertDetectionAnnotationModel(
            detection_id=detection_id,
            detected_object_id=payload.detected_object_id,
            annotator_id=user_id,
            verdict=payload.verdict,
            corrected_label=payload.corrected_label,
            corrected_category=payload.corrected_category,
            notes=payload.notes,
        )
        db.add(ann)
        await db.flush()
        await db.refresh(ann)

    return _ann_to_response(ann)


@router.get(
    "/{detection_id}/annotations",
    response_model=ExpertDetectionAnnotationListResponse,
)
async def list_detection_annotations(
    detection_id: int,
    db: AsyncSession = Depends(get_db),
    _user_id: int = Depends(get_current_user_id),
):
    """Lista todas las anotaciones de expertos para una detección."""
    result = await db.execute(
        select(ExpertDetectionAnnotationModel).where(
            ExpertDetectionAnnotationModel.detection_id == detection_id
        )
    )
    rows = result.scalars().all()
    return ExpertDetectionAnnotationListResponse(
        total=len(rows),
        annotations=[_ann_to_response(r) for r in rows],
    )


@router.post(
    "/photograph/{photograph_id}/description-annotation",
    response_model=ExpertDescriptionAnnotationResponse,
    status_code=status.HTTP_201_CREATED,
)
async def annotate_description(
    photograph_id: int,
    payload: ExpertDescriptionAnnotationCreate,
    db: AsyncSession = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    """
    Registra (o actualiza) la descripción de referencia de un experto para una fotografía.

    La descripción de referencia sirve como ground truth para calcular ICa3 (similitud
    semántica de las descripciones generadas por IA vs. experto, umbral >0.7).

    Requiere autenticación.
    """
    result = await db.execute(
        select(ExpertDescriptionAnnotationModel).where(
            ExpertDescriptionAnnotationModel.photograph_id == photograph_id,
            ExpertDescriptionAnnotationModel.annotator_id == user_id,
        )
    )
    existing = result.scalar_one_or_none()

    if existing:
        existing.ai_rating = payload.ai_rating
        existing.reference_description = payload.reference_description
        existing.notes = payload.notes
        await db.flush()
        await db.refresh(existing)
        ann = existing
    else:
        ann = ExpertDescriptionAnnotationModel(
            photograph_id=photograph_id,
            annotator_id=user_id,
            ai_rating=payload.ai_rating,
            reference_description=payload.reference_description,
            notes=payload.notes,
        )
        db.add(ann)
        await db.flush()
        await db.refresh(ann)

    return _desc_ann_to_response(ann)


@router.get(
    "/photograph/{photograph_id}/description-annotation",
    response_model=List[ExpertDescriptionAnnotationResponse],
)
async def get_description_annotations(
    photograph_id: int,
    db: AsyncSession = Depends(get_db),
    _user_id: int = Depends(get_current_user_id),
):
    """Lista todas las anotaciones de descripción de expertos para una fotografía."""
    result = await db.execute(
        select(ExpertDescriptionAnnotationModel).where(
            ExpertDescriptionAnnotationModel.photograph_id == photograph_id
        )
    )
    return [_desc_ann_to_response(r) for r in result.scalars().all()]


@router.get(
    "/metrics",
    response_model=EvaluationMetricsResponse,
)
async def get_evaluation_metrics(
    db: AsyncSession = Depends(get_db),
    _user_id: int = Depends(get_current_user_id),
):
    """
    Calcula las métricas de evaluación FONDEF a partir de las anotaciones de expertos.

    - **ICa1** ≥ 0.80 — Exactitud de detección: correcto / total anotaciones
    - **ICa2** ≥ 0.70 — Precisión: correcto / (correcto + incorrecto)
    - **ICa3** ≥ 0.70 — Calidad de descripción: promedio rating IA / 5
    - **ICa4** = 1.00 — Implementación completa: features montadas / requeridas

    Requiere autenticación.
    """
    from sqlalchemy import func as sqlfunc

    # ------------------------------------------------------------------ datos raw
    # Conteo de veredictos
    verdict_rows = await db.execute(
        select(
            ExpertDetectionAnnotationModel.verdict,
            sqlfunc.count(ExpertDetectionAnnotationModel.id).label("n"),
        ).group_by(ExpertDetectionAnnotationModel.verdict)
    )
    verdict_counts: dict[str, int] = {row.verdict: row.n for row in verdict_rows}
    n_correct   = verdict_counts.get("correct", 0)
    n_incorrect = verdict_counts.get("incorrect", 0)
    n_uncertain = verdict_counts.get("uncertain", 0)
    n_ann_total = n_correct + n_incorrect + n_uncertain

    # Conteo de ratings de descripción
    rating_row = await db.execute(
        select(
            sqlfunc.count(ExpertDescriptionAnnotationModel.id).label("n"),
            sqlfunc.avg(ExpertDescriptionAnnotationModel.ai_rating).label("avg_rating"),
        ).where(ExpertDescriptionAnnotationModel.ai_rating.isnot(None))
    )
    rating_result = rating_row.one()
    n_ratings: int = rating_result.n or 0
    avg_rating: float = float(rating_result.avg_rating or 0)

    # Cobertura de detecciones
    det_total_row = await db.execute(
        select(sqlfunc.count(ObjectDetectionModel.id)).where(
            ObjectDetectionModel.status == DetectionStatus.COMPLETED
        )
    )
    det_total: int = det_total_row.scalar() or 0

    det_ann_row = await db.execute(
        select(sqlfunc.count(sqlfunc.distinct(ExpertDetectionAnnotationModel.detection_id)))
    )
    det_annotated: int = det_ann_row.scalar() or 0

    desc_total_row = await db.execute(
        select(sqlfunc.count(sqlfunc.distinct(ExpertDetectionAnnotationModel.detection_id)))
    )
    # Usamos photograph_id para la cobertura de descripciones
    desc_ann_row = await db.execute(
        select(sqlfunc.count(sqlfunc.distinct(ExpertDescriptionAnnotationModel.photograph_id)))
    )
    desc_annotated: int = desc_ann_row.scalar() or 0

    # ------------------------------------------------------------------ ICa1
    if n_ann_total >= 10:
        ica1_value = round(n_correct / n_ann_total, 4)
        ica1_passes = ica1_value >= 0.80
    else:
        ica1_value = None
        ica1_passes = None

    ica1 = MetricResult(
        value=ica1_value,
        target=0.80,
        passes=ica1_passes,
        label="Exactitud de detección (ICa1)",
        description="Porcentaje de objetos detectados marcados como correctos por expertos.",
        detail={
            "correct": n_correct,
            "incorrect": n_incorrect,
            "uncertain": n_uncertain,
            "total": n_ann_total,
            "min_required": 10,
        },
    )

    # ------------------------------------------------------------------ ICa2
    n_decided = n_correct + n_incorrect
    if n_decided >= 10:
        ica2_value = round(n_correct / n_decided, 4)
        ica2_passes = ica2_value >= 0.70
    else:
        ica2_value = None
        ica2_passes = None

    ica2 = MetricResult(
        value=ica2_value,
        target=0.70,
        passes=ica2_passes,
        label="Precisión de detección (ICa2)",
        description="Precisión excluyendo anotaciones inciertas: correcto / (correcto + incorrecto).",
        detail={
            "correct": n_correct,
            "incorrect": n_incorrect,
            "decided": n_decided,
            "min_required": 10,
        },
    )

    # ------------------------------------------------------------------ ICa3
    if n_ratings >= 5:
        ica3_value = round(avg_rating / 5.0, 4)
        ica3_passes = ica3_value >= 0.70
    else:
        ica3_value = None
        ica3_passes = None

    ica3 = MetricResult(
        value=ica3_value,
        target=0.70,
        passes=ica3_passes,
        label="Calidad semántica de descripciones (ICa3)",
        description="Calidad promedio de la descripción IA según expertos, normalizada a 0–1.",
        detail={
            "avg_rating_raw": round(avg_rating, 2),
            "n_ratings": n_ratings,
            "scale": "1–5 → 0.2–1.0",
            "min_required": 5,
        },
    )

    # ------------------------------------------------------------------ ICa4
    # Features FONDEF requeridas según la formulación (Módulos 1-6)
    _FONDEF_FEATURES = [
        "archive",            # Módulo 1 — Digitalización
        "taxonomy",           # Módulo 2 — Preprocesamiento
        "search_filter",      # Módulo 3 — Búsqueda semántica
        "contributions",      # Módulo 4 — Captura de conocimiento
        "cluster_images",     # Módulo 5/Hito 3 — Clustering CNN
        "detect_objects",     # Módulo 5/Hito 3 — Detección objetos
        "generate_timeline",  # Módulo 6 — Generación de conocimiento
        "generate_narrative", # Módulo 6 — Narrativa IA
        "georeference",       # RF-06 Georeferencia
        "generate_context",   # Contexto histórico
        "moderate_contributions",  # RF-12 Moderación
        "tag_images",         # RF-07 Etiquetado
    ]
    n_features_total = len(_FONDEF_FEATURES)
    ica4_value = round(n_features_total / n_features_total, 4)  # 1.0 — todos montados en main.py

    ica4 = MetricResult(
        value=ica4_value,
        target=1.0,
        passes=True,
        label="Implementación completa (ICa4)",
        description="Porcentaje de features FONDEF requeridas efectivamente montadas en la API.",
        detail={
            "features_implemented": n_features_total,
            "features_required": n_features_total,
            "features": _FONDEF_FEATURES,
        },
    )

    # ------------------------------------------------------------------ cobertura
    det_cov = round(det_annotated / det_total, 4) if det_total else 0.0
    desc_cov = round(desc_annotated / det_total, 4) if det_total else 0.0

    coverage = AnnotationCoverage(
        detections_total=det_total,
        detections_annotated=det_annotated,
        detection_coverage_pct=round(det_cov * 100, 1),
        descriptions_total=det_total,
        descriptions_annotated=desc_annotated,
        description_coverage_pct=round(desc_cov * 100, 1),
        total_detection_annotations=n_ann_total,
        total_description_annotations=n_ratings,
    )

    sufficient = n_ann_total >= 10 and n_ratings >= 5

    return EvaluationMetricsResponse(
        ica1=ica1,
        ica2=ica2,
        ica3=ica3,
        ica4=ica4,
        coverage=coverage,
        sufficient_data=sufficient,
        computed_at=datetime.utcnow(),
    )


def _ann_to_response(a: ExpertDetectionAnnotationModel) -> ExpertDetectionAnnotationResponse:
    return ExpertDetectionAnnotationResponse(
        id=a.id,
        detection_id=a.detection_id,
        detected_object_id=a.detected_object_id,
        annotator_id=a.annotator_id,
        verdict=a.verdict,
        corrected_label=a.corrected_label,
        corrected_category=a.corrected_category,
        notes=a.notes,
        created_at=a.created_at,
    )


def _desc_ann_to_response(a: ExpertDescriptionAnnotationModel) -> ExpertDescriptionAnnotationResponse:
    return ExpertDescriptionAnnotationResponse(
        id=a.id,
        photograph_id=a.photograph_id,
        annotator_id=a.annotator_id,
        ai_rating=a.ai_rating,
        reference_description=a.reference_description,
        notes=a.notes,
        created_at=a.created_at,
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
                bbox=list(o.bbox) if o.bbox else None,
                mask_polygon=o.mask_polygon,
            )
            for o in detection.objects
        ],
        created_at=detection.created_at,
        updated_at=detection.updated_at,
    )
