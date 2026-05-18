from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.features.cluster_images.application.cluster_images_usecase import ClusterImagesUseCase
from app.features.cluster_images.domain.cluster import ClusterAlgorithm, ClusteringJob
from app.features.cluster_images.infrastructure.adapters.cluster_repository import ClusterRepository
from app.features.cluster_images.infrastructure.adapters.clustering_engine import ClusteringEngine
from app.features.cluster_images.interfaces.api.schemas import (
    ClusterRequest, ClusterResponse, ClusteringJobListResponse, ClusteringJobResponse,
)
from app.infrastructure.database.session import get_db
from app.shared.domain.exceptions import EntityNotFoundError

router = APIRouter(prefix="/clusters", tags=["Clustering"])


def _build_usecase(db: AsyncSession) -> ClusterImagesUseCase:
    return ClusterImagesUseCase(
        engine=ClusteringEngine(),
        repository=ClusterRepository(db),
    )


@router.post("", response_model=ClusteringJobResponse, status_code=status.HTTP_201_CREATED)
async def cluster_photographs(
    request: ClusterRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Agrupa fotografías por similitud semántica usando sentence-transformers.

    - **photograph_ids**: lista de IDs de fotografías (mínimo 2)
    - **algorithm**: dbscan (automático, detecta outliers) | kmeans (requiere n_clusters)
    - **n_clusters**: solo para kmeans; si se omite en dbscan, se detecta automáticamente
    - **texts**: descripciones textuales por fotografía (mismo orden). Si se omiten,
      provee textos desde los metadatos antes de llamar este endpoint para mejores resultados.

    Requiere autenticación. Pensado para grupos de trabajo de investigadores.
    """
    try:
        alg = ClusterAlgorithm(request.algorithm)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Algoritmo '{request.algorithm}' no válido. Opciones: dbscan, kmeans",
        )

    try:
        usecase = _build_usecase(db)
        job = await usecase.execute(
            photograph_ids=request.photograph_ids,
            algorithm=alg,
            n_clusters=request.n_clusters,
            texts=request.texts,
        )
        return _to_response(job)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/{job_id}", response_model=ClusteringJobResponse)
async def get_clustering_job(
    job_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Retorna los resultados de un job de clustering por ID."""
    try:
        usecase = _build_usecase(db)
        job = await usecase.get(job_id)
        return _to_response(job)
    except EntityNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.get("", response_model=ClusteringJobListResponse)
async def list_clustering_jobs(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    """Lista todos los jobs de clustering con paginación."""
    repository = ClusterRepository(db)
    jobs = await repository.list(skip, limit)
    return ClusteringJobListResponse(
        total=len(jobs),
        skip=skip,
        limit=limit,
        jobs=[_to_response(j) for j in jobs],
    )


@router.delete("/{job_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_clustering_job(
    job_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Elimina un job de clustering y todos sus clusters."""
    repository = ClusterRepository(db)
    deleted = await repository.delete(job_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Job de clustering {job_id} no encontrado",
        )


@router.post("/{job_id}/justify", response_model=ClusteringJobResponse)
async def justify_clustering_job(
    job_id: int,
    db: AsyncSession = Depends(get_db),
):
    """
    Genera mediante el LLM configurado (Groq por default) una justificación breve
    (2-3 líneas) que explica el patrón visual común que llevó a agrupar las
    fotografías de cada cluster. Persiste la justificación en cada cluster y
    devuelve el job actualizado.

    Idempotente: re-llamarlo regenera todas las justificaciones.
    """
    from app.features.archive.infrastructure.persistence.archive_model import PhotographModel
    from app.infrastructure.ai.llm.llm_factory import create_llm_provider
    from sqlalchemy.future import select as _sel

    repository = ClusterRepository(db)
    job = await repository.get_by_id(job_id)
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Job de clustering {job_id} no encontrado",
        )

    try:
        llm = create_llm_provider()
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"LLM no disponible: {e}",
        )

    # Carga metadatos de todas las fotografías involucradas en una sola query
    all_ids = {pid for c in job.clusters for pid in c.photograph_ids}
    photo_meta: dict[int, dict] = {}
    if all_ids:
        result = await db.execute(
            _sel(PhotographModel).where(PhotographModel.id.in_(all_ids))
        )
        for p in result.scalars().all():
            photo_meta[p.id] = {
                "identifier": p.identifier,
                "frame_number": p.frame_number,
                "internal_cronology": p.internal_cronology,
                "physical_location_ref": p.physical_location_ref,
            }

    system_prompt = (
        "Eres un asistente curatorial para un archivo fotográfico patrimonial. "
        "Dado un grupo de fotografías agrupadas por similitud semántica visual, "
        "explica en 2-3 líneas concisas y en español qué tienen en común desde "
        "una perspectiva curatorial: período, tema, lugar, técnica o motivo. "
        "Sé específico cuando los metadatos lo permitan. Si la información es "
        "escasa, indícalo brevemente. Nunca inventes fuentes ni datos."
    )

    for cluster in job.clusters:
        photo_descs = []
        for pid in cluster.photograph_ids[:20]:  # limita contexto
            meta = photo_meta.get(pid, {})
            parts = [f"id={pid}"]
            if meta.get("identifier"):
                parts.append(f"ref={meta['identifier']}")
            if meta.get("internal_cronology"):
                parts.append(f"cronología={meta['internal_cronology']}")
            if meta.get("physical_location_ref"):
                parts.append(f"ubicación={meta['physical_location_ref']}")
            photo_descs.append(" · ".join(parts))

        if len(cluster.photograph_ids) > 20:
            photo_descs.append(f"… y {len(cluster.photograph_ids) - 20} más")

        user_prompt = (
            f"Cluster: {cluster.label}\n"
            f"Algoritmo: {cluster.algorithm.value}\n"
            f"{cluster.member_count} fotografías:\n- "
            + "\n- ".join(photo_descs)
            + "\n\n¿Qué tienen en común estas fotografías?"
        )

        try:
            justification = await llm.complete([
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ])
            cluster.justification = justification.strip()
            if cluster.id is not None:
                await repository.update_cluster_justification(cluster.id, cluster.justification)
        except Exception as e:
            # No exponer el error real al usuario — solo loggear y guardar mensaje genérico
            import structlog
            structlog.get_logger().warning(
                "LLM justify failed",
                cluster_id=cluster.id,
                job_id=job_id,
                error=str(e),
            )
            cluster.justification = None
            if cluster.id is not None:
                await repository.update_cluster_justification(cluster.id, None)

    await db.commit()
    return _to_response(job)


def _to_response(job: ClusteringJob) -> ClusteringJobResponse:
    return ClusteringJobResponse(
        id=job.id,
        algorithm=job.algorithm.value,
        embedding_model=job.embedding_model,
        n_clusters=job.n_clusters,
        noise_count=job.noise_count,
        processing_time_ms=job.processing_time_ms,
        status=job.status.value,
        photograph_ids=job.photograph_ids,
        clusters=[
            ClusterResponse(
                id=c.id,
                label=c.label,
                algorithm=c.algorithm.value,
                member_count=c.member_count,
                centroid_photograph_id=c.centroid_photograph_id,
                photograph_ids=c.photograph_ids,
                status=c.status.value,
                justification=c.justification,
            )
            for c in job.clusters
        ],
        created_at=job.created_at,
        updated_at=job.updated_at,
    )
