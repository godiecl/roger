from typing import List, Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.features.detect_objects.domain.detection import (
    Detection, DetectedObject, DetectionStatus, ObjectCategory,
)
from app.features.detect_objects.domain.detection_port import IDetectionRepository
from app.features.detect_objects.infrastructure.persistence.detection_model import (
    ObjectDetectionModel, DetectedObjectModel,
)


class DetectionRepository(IDetectionRepository):

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, detection: Detection) -> Detection:
        model = ObjectDetectionModel(
            photograph_id=detection.photograph_id,
            provider=detection.provider,
            scene_description=detection.scene_description,
            detection_time_ms=detection.detection_time_ms,
            status=DetectionStatus(detection.status),
        )
        self.session.add(model)
        await self.session.flush()
        await self.session.refresh(model)

        obj_models = []
        for obj in detection.objects:
            bbox = obj.bbox or (None, None, None, None)
            obj_model = DetectedObjectModel(
                detection_id=model.id,
                label=obj.label,
                category=ObjectCategory(obj.category),
                confidence=obj.confidence,
                description=obj.description,
                bbox_x1=bbox[0],
                bbox_y1=bbox[1],
                bbox_x2=bbox[2],
                bbox_y2=bbox[3],
                mask_polygon=obj.mask_polygon,
            )
            self.session.add(obj_model)
            obj_models.append(obj_model)

        await self.session.flush()

        detection.id = model.id
        detection.created_at = model.created_at
        detection.updated_at = model.updated_at
        for i, obj_model in enumerate(obj_models):
            await self.session.refresh(obj_model)
            detection.objects[i].id = obj_model.id

        return detection

    async def get_by_id(self, detection_id: int) -> Optional[Detection]:
        result = await self.session.execute(
            select(ObjectDetectionModel).where(ObjectDetectionModel.id == detection_id)
        )
        model = result.scalar_one_or_none()
        return await self._to_domain(model) if model else None

    async def get_by_photograph(self, photograph_id: int) -> Optional[Detection]:
        result = await self.session.execute(
            select(ObjectDetectionModel)
            .where(ObjectDetectionModel.photograph_id == photograph_id)
            .order_by(ObjectDetectionModel.id.desc())
            .limit(1)
        )
        model = result.scalar_one_or_none()
        return await self._to_domain(model) if model else None

    async def list(self, skip: int, limit: int) -> List[Detection]:
        result = await self.session.execute(
            select(ObjectDetectionModel)
            .order_by(ObjectDetectionModel.id.desc())
            .offset(skip)
            .limit(limit)
        )
        return [await self._to_domain(m) for m in result.scalars().all()]

    async def delete(self, detection_id: int) -> bool:
        result = await self.session.execute(
            select(ObjectDetectionModel).where(ObjectDetectionModel.id == detection_id)
        )
        model = result.scalar_one_or_none()
        if not model:
            return False
        await self.session.delete(model)
        await self.session.flush()
        return True

    async def _to_domain(self, model: ObjectDetectionModel) -> Detection:
        objs_result = await self.session.execute(
            select(DetectedObjectModel).where(DetectedObjectModel.detection_id == model.id)
        )
        objects = []
        for o in objs_result.scalars().all():
            bbox = None
            if o.bbox_x1 is not None:
                bbox = (o.bbox_x1, o.bbox_y1, o.bbox_x2, o.bbox_y2)
            objects.append(DetectedObject(
                id=o.id,
                label=o.label,
                category=ObjectCategory(o.category),
                confidence=o.confidence,
                description=o.description,
                bbox=bbox,
                mask_polygon=o.mask_polygon,
            ))
        return Detection(
            id=model.id,
            photograph_id=model.photograph_id,
            provider=model.provider,
            scene_description=model.scene_description or "",
            detection_time_ms=model.detection_time_ms or 0,
            status=DetectionStatus(model.status),
            objects=objects,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )
