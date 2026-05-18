import hashlib
from datetime import datetime
from typing import Optional, List

from sqlalchemy import select, delete, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

from app.features.generate_context.domain.context import ImageContext
from app.features.generate_context.domain.context_port import IContextRepository
from app.features.generate_context.infrastructure.persistence.context_model import ImageContextModel
from app.features.generate_context.infrastructure.persistence.like_model import ContentLikeModel
from app.features.generate_context.infrastructure.persistence.report_model import ContentReportModel


def _to_domain(m: ImageContextModel) -> ImageContext:
    return ImageContext(
        id=m.id,
        image_id=m.image_id,
        text=m.text,
        provider=m.provider,
        generation_time_ms=m.generation_time_ms,
        is_anchored=m.is_anchored,
        anchored_by=m.anchored_by,
        anchored_at=m.anchored_at,
        like_count=m.like_count,
        report_count=m.report_count,
        created_at=m.created_at,
        updated_at=m.updated_at,
    )


class ContextRepository(IContextRepository):
    def __init__(self, db: AsyncSession):
        self._db = db

    async def save(self, context: ImageContext) -> ImageContext:
        model = ImageContextModel(
            image_id=context.image_id,
            text=context.text,
            provider=context.provider,
            generation_time_ms=context.generation_time_ms,
        )
        self._db.add(model)
        await self._db.flush()
        await self._db.refresh(model)
        return _to_domain(model)

    async def get_anchored(self, image_id: int) -> List[ImageContext]:
        result = await self._db.execute(
            select(ImageContextModel)
            .where(ImageContextModel.image_id == image_id, ImageContextModel.is_anchored == True)
            .order_by(ImageContextModel.like_count.desc())
        )
        return [_to_domain(r) for r in result.scalars().all()]

    async def get_by_id(self, context_id: int) -> Optional[ImageContext]:
        result = await self._db.execute(
            select(ImageContextModel).where(ImageContextModel.id == context_id)
        )
        model = result.scalar_one_or_none()
        return _to_domain(model) if model else None

    async def anchor(self, context_id: int, user_id: int) -> ImageContext:
        result = await self._db.execute(
            select(ImageContextModel).where(ImageContextModel.id == context_id)
        )
        model = result.scalar_one_or_none()
        if not model:
            raise ValueError(f"Context {context_id} not found")
        model.is_anchored = True
        model.anchored_by = user_id
        model.anchored_at = datetime.utcnow()
        await self._db.flush()
        return _to_domain(model)

    async def unanchor(self, context_id: int) -> ImageContext:
        result = await self._db.execute(
            select(ImageContextModel).where(ImageContextModel.id == context_id)
        )
        model = result.scalar_one_or_none()
        if not model:
            raise ValueError(f"Context {context_id} not found")
        model.is_anchored = False
        model.anchored_by = None
        model.anchored_at = None
        await self._db.flush()
        return _to_domain(model)

    async def toggle_like(self, context_id: int, ip_hash: str) -> tuple[bool, int]:
        result = await self._db.execute(
            select(ContentLikeModel).where(
                ContentLikeModel.content_type == "context",
                ContentLikeModel.content_id == context_id,
                ContentLikeModel.ip_hash == ip_hash,
            )
        )
        existing = result.scalar_one_or_none()

        ctx_result = await self._db.execute(
            select(ImageContextModel).where(ImageContextModel.id == context_id)
        )
        ctx = ctx_result.scalar_one_or_none()
        if not ctx:
            raise ValueError(f"Context {context_id} not found")

        if existing:
            await self._db.delete(existing)
            ctx.like_count = max(0, ctx.like_count - 1)
            await self._db.flush()
            return False, ctx.like_count
        else:
            like = ContentLikeModel(content_type="context", content_id=context_id, ip_hash=ip_hash)
            self._db.add(like)
            ctx.like_count += 1
            await self._db.flush()
            return True, ctx.like_count

    async def add_report(self, context_id: int, ip_hash: str, reason: Optional[str]) -> bool:
        ctx_result = await self._db.execute(
            select(ImageContextModel).where(ImageContextModel.id == context_id)
        )
        ctx = ctx_result.scalar_one_or_none()
        if not ctx:
            raise ValueError(f"Context {context_id} not found")

        report = ContentReportModel(
            content_type="context",
            content_id=context_id,
            ip_hash=ip_hash,
            reason=reason,
        )
        self._db.add(report)
        try:
            await self._db.flush()
            ctx.report_count += 1
            await self._db.flush()
            return True
        except IntegrityError:
            await self._db.rollback()
            return False  # already reported

    async def list_pending(self, skip: int, limit: int) -> List[ImageContext]:
        result = await self._db.execute(
            select(ImageContextModel)
            .where(ImageContextModel.is_anchored == False, ImageContextModel.like_count > 0)
            .order_by(ImageContextModel.like_count.desc())
            .offset(skip)
            .limit(limit)
        )
        return [_to_domain(r) for r in result.scalars().all()]

    async def count_pending_reports(self) -> int:
        result = await self._db.execute(
            select(func.count()).where(ContentReportModel.status == "pending")
        )
        return result.scalar_one() or 0
