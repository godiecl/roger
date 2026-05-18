"""
Seed minimal data for testing /archivo flow.
Run: python -m scripts.seed_archive_test
"""
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy.ext.asyncio import async_sessionmaker
from app.infrastructure.database.session import engine, init_db
from app.features.authenticate.infrastructure.persistence.user_model import UserModel
from app.features.authenticate.domain.role import Role
from app.features.authenticate.infrastructure.adapters.password_hasher import password_hasher
from app.features.view_images.infrastructure.persistence.image_model import CollectionModel
from app.features.archive.infrastructure.persistence.archive_model import (
    BoxModel, RollModel, PhotographModel,
)


async def main():
    await init_db()
    Session = async_sessionmaker(engine, expire_on_commit=False, autocommit=False, autoflush=False)
    async with Session() as session:
        # Admin user
        admin = UserModel(
            email="admin@roger.cl",
            username="admin",
            hashed_password=password_hasher.hash("admin123"),
            role=Role.ADMINISTRADOR,
            full_name="Admin Test",
            is_active=True,
            is_verified=True,
        )
        session.add(admin)
        await session.flush()

        # Collection
        col = CollectionModel(
            name="Robert Gerstmann (test)",
            slug="gerstmann-test",
            description="Colección de prueba para /archivo",
            photographer_name="Robert Gerstmann",
            origin_country="Chile",
            is_public=True,
            created_by=admin.id,
        )
        session.add(col)
        await session.flush()

        # 2 boxes
        boxes = []
        for i in (1, 2):
            box = BoxModel(
                collection_id=col.id,
                box_number=i,
                name=f"Cajón {i} de prueba",
                location_in_archive=f"Estante A-{i}",
            )
            session.add(box)
            boxes.append(box)
        await session.flush()

        # 1 roll per box, 8 photos per roll
        for box in boxes:
            roll = RollModel(
                box_id=box.id,
                general_number=box.box_number * 10,
                internal_number=1,
                name=f"Rollo {box.box_number}-1",
                image_type="neg",
                support="flex",
                physical_status="good",
                color_mode="bw",
                frame_count=8,
            )
            session.add(roll)
            await session.flush()

            for frame in range(1, 9):
                photo = PhotographModel(
                    roll_id=roll.id,
                    frame_number=frame,
                    identifier=f"GER-{box.box_number:02d}-{frame:03d}",
                    internal_cronology=str(1928 + (frame % 4)),
                    physical_location_ref="Antofagasta" if frame % 2 == 0 else "Atacama",
                    is_public=True,
                )
                session.add(photo)

        await session.commit()
        print(f"Seeded admin id={admin.id}, collection id={col.id}")
        print(f"  Boxes: {[b.id for b in boxes]}")
        print(f"  Photos: 16 total (8 per box)")
        print(f"\nLogin: admin@roger.cl / admin123")


if __name__ == "__main__":
    asyncio.run(main())
