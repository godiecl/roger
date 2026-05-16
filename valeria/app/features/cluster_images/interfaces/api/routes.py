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
            )
            for c in job.clusters
        ],
        created_at=job.created_at,
        updated_at=job.updated_at,
    )
